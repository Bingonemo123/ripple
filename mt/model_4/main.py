import MetaTrader5 as connector
import logging.handlers
import logging
import time
import sys
import os
import pathlib
import json
from model_3 import mathfc as mathf
from pushover import Client
from model_3 import timeout

prc = 'pract' in sys.argv

class Model():
    def __init__ (self):

        self.modeln = 4.1
       
        '''----------------------------------------------------------------------------------------------'''
        if os.name == 'posix':
            self.path = pathlib.PurePosixPath(os.path.abspath(__file__)).parent
        else:
            self.path = pathlib.PureWindowsPath(os.path.abspath(__file__)).parent
        '''----------------------------------------------------------------------------------------------'''
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        """StreamHandler"""
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG) 
        stream_handler.setFormatter(formatter)
        self.logger.addHandler(stream_handler)
        """FileHandler"""
        rotatingfile_handler = logging.handlers.RotatingFileHandler(self.path/f'main{prc * "_prc"}.log', backupCount=5, maxBytes=1073741824)
        rotatingfile_handler.setLevel(logging.DEBUG)
        rotatingfile_handler.setFormatter(formatter)
        self.logger.addHandler(rotatingfile_handler)
        #----------------------------------------------------------------------------#
        self.client = Client("ud1pmkki74te12d3bicw24r99kb38z", api_token="aq7rx1r3o55k6rtobcq8xwv66u8jgw")

    def login (self, credentials):
        self.credentials = credentials
        
        if not connector.initialize():
            print("initialize() failed")
            connector.shutdown()

        account = self.credentials[0]
        password = self.credentials[1]
        server = self.credentials[2]
        authorized = connector.login(account, password=password, server=server)
        if not authorized:
            print("failed to connect at account #{}, error code: {}".format(
                account, connector.last_error()))

    #----------------------------------------------------------------------------#
    def run(self):
        
        self.client.send_message(os.getcwd(), title=f"M{prc * 'P'}{self.modeln} I0")
        #----------------------------------------------------------------------------#
        datapath = self.path/f'data{prc * "_prc"}.json'
        try:
            data = json.load(open(datapath, 'r'))
        except FileNotFoundError:
            data = []
            json.dump(data, open(datapath, 'w'))

        means_data = json.load(open(self.path/'month_means.json', 'r'))
        #----------------------------------------------------------------------------#
        while True:
            try:
                ### Refresh Data
                json.dump(data, open(datapath, 'w'))

                ### Cut Out
                cutout = 4
                for d in data[::-1]:
                    if d.get("Name") == 'Cut Out':
                        sttime = d.get("Time")
                        if (time.time() - sttime) >= (cutout * 3600 ):
                            pmm = timeout.custom_profit(connector)
                            if isinstance(pmm, (str, Exception)):
                                self.logger.info(f'M{self.modeln}Sk1 Reason: {pmm}')
                                break
        
                            total_profit, total_margin, msg = pmm
                            self.logger.info(f'TP: {total_profit}')
                            if total_profit > 0:
                                data.append({'Name' : 'Cut Out',
                                        'Id' : d.get('Id') + 1,
                                        'Time': time.time(),
                                        'Profit': total_profit,
                                        'Investment': total_margin,
                                        'Total Positions': len(msg),
                                        'Time Delta': round((time.time() - sttime)/3600, 3)
                                    })
                                json.dump(data, open(datapath, 'w'))
                                for position in msg:
                                    clres = timeout.custom_close(connector, position)
                                    if clres is not True:
                                        self.logger.info(f'M{self.modeln}Sk2 Reason: {clres}')
                                self.logger.info(str(data[-1]))
                                self.client.send_message(str(data[-1]), title=f"M{prc * 'P'}{self.modeln} {os.getcwd()}")
                        break
                else:
                    data.append({'Name' : 'Cut Out',
                                        'Id' : 1,
                                        'Time': time.time(),
                                        'Profit': None,
                                        'Investment': None,
                                        'Total Positions': None,
                                        'Time Delta': None
                                    })
                    json.dump(data, open(datapath, 'w'))
                    self.logger.info(str(data[-1]))

                ### Open Assets 

                ALL_Asset=timeout.custom_all_asets(connector)
                if isinstance(ALL_Asset, (str, Exception)):
                    self.logger.info(f'M{self.modeln}Sk3 Reason: {ALL_Asset}')
                    continue

            
                open_s = []

                for x in ALL_Asset:
                    sft = timeout.custom_safty(connector, x.name)
                    if not isinstance(sft, bool):
                        self.logger.info(f'M{self.modeln}Sk4 Reason: {sft}')
                        continue
                    if sft:
                        open_s.append(x.name)
                

                ### Filter new positions
                delay = 8
                Filter = []

                pmm = timeout.custom_profit(connector)
                if isinstance(pmm, (str, Exception)):
                    self.logger.info(f'M{self.modeln}Sk5 Reason: {pmm}')
                    break

                total_profit, total_margin, msg = pmm
                poshold = [pos.symbol for pos in msg]

                for f in open_s:
                    if f in poshold:
                        continue
                    for d in data[::-1]:
                        if d.get('Name') == f:
                            if (time.time() - d.get('Buying_time', 0)) > delay * 3600:
                                Filter.append(f)
                            break
                    else:
                        Filter.append(f)

                open_s = Filter
                #Get real time prices 
                
                checklist = []
                pricelist = []
                leverages = []

                for f in open_s:
                    price = timeout.custom_price(connector, f)
                    if not isinstance(price, (float, int)):
                        self.logger.info(f'M{self.modeln}Sk6 Reason: {price}')
                        continue
                    fleverage = timeout.custom_leverage(connector)
                    if not isinstance(fleverage, (float, int)):
                        self.logger.info(f'M{self.modeln}Sk7 Reason: {fleverage}')
                        continue

                    checklist.append(f)
                    pricelist.append(price)
                    leverages.append(fleverage)

                balance = timeout.get_custom_balance(connector)
                if not isinstance(balance, (float, int)):
                    self.logger.info(f'M{self.modeln}Sk8 Reason: {balance}')
                    continue
                
                self.logger.info(f'Balance: {balance}')
                self.logger.info(f'Possible Symbols number: {len(open_s)}')
                foundmark = mathf.EZAquariiB(checklist, pricelist, means_data, leverages, balance)
                if foundmark == None:
                    self.logger.info(f'M{self.modeln} SE1 [winter sleep]')
                    time.sleep(60*3)
                    continue
                self.logger.info(foundmark)
                
                name, m, n, leverage = foundmark[1]

                if balance/(leverage * n) < 1:
                    self.logger.info(f'M{self.modeln} SE2 [balance shortage]')
                    amount = 1
                elif balance/ (leverage * n) > 20000:
                    amount = 20000
                else:
                    amount = balance/ (leverage * n)

                take_profit_value = int( 100 * m )

                #### ORDER ####
                cpbh =  timeout.custom_prebuy(connector, name)
                if not isinstance(cpbh, tuple):
                    self.logger.info(f'M{self.modeln}Sk9 Reason: {cpbh}')
                    continue

                point, volume_step, price, margin, volume_max = cpbh

                volume = amount / margin
                if volume > volume_max:
                    volume = volume_max
                volume = (volume // volume_step) * volume_step

                closing_price =  ((m/leverage) + 1) * price
                closing_price = (closing_price // point ) * point
                if closing_price < price:
                    closing_price = 0

                request = {
                        "action": connector.TRADE_ACTION_DEAL,
                        "symbol": name,
                        "volume": volume,
                        "type": connector.ORDER_TYPE_BUY,
                        "price": price,
                        # "sl": 0,
                        "tp": closing_price,
                        "comment": f"Placed by model {self.modeln}",
                        "type_time": connector.ORDER_TIME_GTC,
                        "type_filling": connector.ORDER_FILLING_IOC,
                }

                check = connector.order_send(request)

                if check.comment == 'No prices':
                    avvol = timeout.custom_volmeter(connector, f)
                    if not isinstance(avvol, (float, int)):
                        self.logger.info(f'M{self.modeln}Sk10 Reason: {avvol}')
                        request['Name'] = name
                        request['Buying_time'] = time.time()
                        data.append(request)
                        continue
                    request['volume'] = avvol
                    check = connector.order_send(request)

                if check.comment == 'Invalid stops':
                    del request['tp']
                    check = connector.order_send(request)

                if check.comment == 'Market closed':
                    data.append({'Name' : name,
                                    'Id' : 'Market closed',
                                    'Buying_time': time.time(),
                                    'Amount': amount,
                                    'Balance': balance,
                                    'leverage': leverage,
                                    'TakeProfitValue': take_profit_value,
                                    'Position_Id': 'Market closed'
                                }) # add exam


                elif check.retcode != connector.TRADE_RETCODE_DONE:
                    self.logger.warning("2. order_send failed, retcode={}".format(check.retcode))
                    # request the result as a dictionary and display it element by element
                    result_dict=check._asdict()
                    for field in result_dict.keys():
                        self.logger.warning("   {}={}".format(field,result_dict[field]))
                        # if this is a trading request structure, display it element by element as well
                        if field=="request":
                            traderequest_dict=result_dict[field]._asdict()
                            for tradereq_filed in traderequest_dict:
                                self.logger.warning("       traderequest: {}={}".format(tradereq_filed,traderequest_dict[tradereq_filed]))
                    
                    request['Name'] = name
                    request['Cause'] = check.comment
                    request['Buying_time'] = time.time()
                    data.append(request)
                    continue

                else:
                    self.logger.info(check.comment)
                    position_id = check.order
                    data.append({'Name' : name,
                                    'Id' : position_id,
                                    'Buying_time': time.time(),
                                    'Amount': amount,
                                    'Balance': balance,
                                    'leverage': leverage,
                                    'TakeProfitValue': take_profit_value,
                                    'Position_Id': position_id
                                }) # add exam
                json.dump(data, open(datapath, 'w'))
                self.logger.info(f'Total elements in data: {len(data)}')
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                self.logger.exception(str(e))
                self.logger.exception([exc_type, fname, exc_tb.tb_lineno])
                self.client.send_message(exc_type, title=f'M{prc * "P"}{self.modeln}E {os.getcwd()}')
                self.logger.info(f'M{self.modeln} SE3 [Error hold]')
                time.sleep(60*3)

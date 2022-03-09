from iqoptionapi.stable_api import IQ_Option
import Internet_protocols
import logging.handlers
import datetime
import pathlib
import logging
import time
import sys
import operator
import os
connector =IQ_Option("ww.bingonemo@gmail.com","JF*#3C5va&_NDqy")
connector.connect()
       
'''----------------------------------------------------------------------------------------------'''

if os.name == 'posix':
    path = pathlib.PurePosixPath(os.path.abspath(__file__)).parent 
    if 'Forex_experiments' in path.parts:
        path = path.parent / str(datetime.date.today())
    else:
        path = path / 'Forex_experiments'  / str(datetime.date.today())
    # After this, path is equals to current date folder
    file_path = pathlib.PurePosixPath(os.path.abspath(__file__))
else:
    path = pathlib.PureWindowsPath(os.path.abspath(__file__)).parent 
    if 'Forex_experiments' in path.parts:
        path = path.parent / str(datetime.date.today())
    else:
        path = path / 'Forex_experiments'  / str(datetime.date.today())
    # After this, path is equals to current date folder
    file_path = pathlib.PureWindowsPath(os.path.abspath(__file__))
'''----------------------------------------------------------------------------------------------'''
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
"""StreamHandler"""
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG) 
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
"""FileHandler"""
rotatingfile_handler = logging.handlers.RotatingFileHandler(path.parent/'main.log', backupCount=5, maxBytes=1073741824)
rotatingfile_handler.setLevel(logging.DEBUG)
rotatingfile_handler.setFormatter(formatter)
logger.addHandler(rotatingfile_handler)

#----------------------------------------------------------------------------#
#----------------------------------------------------------------------------#
def historyd():
    try:
        pass
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        Internet_protocols.email(str(e), subj='Error')
        logger.exception(str(e))
        logger.exception([exc_type, fname, exc_tb.tb_lineno])
        time.sleep(60*3)

def stocks_mm():
    connector.update_ACTIVES_OPCODE()
    opcode_data=connector.get_all_ACTIVES_OPCODE()

    instrument_type='forex'
    connector.subscribe_top_assets_updated(instrument_type)
    
    def opcode_to_name(opcode_data,opcode):
        return list(opcode_data.keys())[list(opcode_data.values()).index(opcode)]            

    while True:
        if connector.get_top_assets_updated(instrument_type)!=None:
            break

    top_assets=connector.get_top_assets_updated(instrument_type)

    for asset in top_assets:
        print(asset, " <<<<>>>>>")

    diff_trading_day={}
    for asset in top_assets:
        opcode=asset["active_id"]
        diff_trading_day_value=asset["diff_trading_day"]["value"]
        try:
            name=opcode_to_name(opcode_data,opcode)
            diff_trading_day[name]=diff_trading_day_value
        except:
            pass
    
    sorted_diff_trading_day= sorted(diff_trading_day.items(), key=operator.itemgetter(1))

    return ([x[0] for x in reversed(sorted_diff_trading_day)])
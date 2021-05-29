import time
from iqoptionapi.stable_api import IQ_Option
I_want_money=IQ_Option("ww.bingonemo@gmail.com","JF*#3C5va&_NDqy")
I_want_money.connect()#connect to iqoption
#instrument_type: "binary-option"/"turbo-option"/"digital-option"/"crypto"/"forex"/"cfd"
instrument_type=["binary-option","turbo-option","digital-option","crypto","forex","cfd"]
instrument_type=["forex"]
for ins in instrument_type:
    I_want_money.subscribe_commission_changed(ins)
print("Start stream please wait profit change...")
while True:
    for ins in instrument_type:
        commissio_data=I_want_money.get_commission_change(ins)
        if commissio_data!={}:
            for active_name in commissio_data:
                if commissio_data[active_name]!={}:
                    the_min_timestamp=min(commissio_data[active_name].keys())
                    commissio=commissio_data[active_name][the_min_timestamp]
                    profit=(100-commissio)/100
                    print("instrument_type: "+str(ins)+" active_name: "+str(active_name)+" profit change to: "+str(profit))
                    #Data have been update so need del
                    del I_want_money.get_commission_change(ins)[active_name][the_min_timestamp]
    time.sleep(1)

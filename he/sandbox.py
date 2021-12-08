from pushover import Client
import os 
import time
client = Client("ud1pmkki74te12d3bicw24r99kb38z", api_token="aq7rx1r3o55k6rtobcq8xwv66u8jgw")
client.send_message(os.getcwd(), title="M1 I0")
data = []
data.append({'Name' : 'Cut Out',
                                'Id' : 1,
                                'Time': time.time(),
                                'Profit': None,
                                'Investment': None,
                                'Total Positions': None,
                                'Time Delta': None
                            })
client.send_message(str(data[-1]), title=f"M1 {os.getcwd()}")

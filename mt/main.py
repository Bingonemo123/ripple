from model_4.main import Model 
from credentials import FxPro
m = Model()
m.login(FxPro['Account 1'])
m.run()
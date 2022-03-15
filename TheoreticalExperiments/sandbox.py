
from datetime import datetime

j =[ datetime.now(), "ERUSD", 18305.304]

for x in j:
    if isinstance(x, float):
        x = f'{x:,.2f}'
    print(f"{f'{x}':^30}")



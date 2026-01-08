
from io import StringIO
import pandas as pd
from preparedata import prepare_data
from gridding import linear_grid


data = prepare_data(base_url="someURL",username="username",password="pwd",dx='jPEcKbn7jmh',pe="202501",ou_level="4")
dataValues = pd.read_csv(StringIO(data))
lin = linear_grid(dataValues)

print(lin.head)

from database import DataBase
from fpgrowth import FPGrowth

import time

ini = time.time()

db = DataBase.read_csv('test.csv', ';')

def getKey(i):
    return i.split(',')

conj_desc_erro = db.get_column('erros', key=getKey)

transactions = DataBase.transaction_encoder(conj_desc_erro)

fpGrowth = FPGrowth(transactions, 0.45)

end = time.time()

print(end - ini)
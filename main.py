from database import DataBase
from fpgrowth import FPGrowth

import time

ini = time.time()

db = DataBase.read_csv('test.csv', ';')

conj_desc_erro = db.get_column('compras', key=lambda i: i.split(','))

transactions = DataBase.transaction_encoder(conj_desc_erro)

fpGrowth = FPGrowth(transactions, 0.5)

end = time.time()

print(end - ini)
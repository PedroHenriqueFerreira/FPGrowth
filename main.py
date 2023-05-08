from database import DataBase
from fpgrowth import FPGrowth

db = DataBase.read_csv('teste.csv', ';')

conj_desc_erro = db.get_column('compras', key=lambda i: i.split(','))

transactions = DataBase.transaction_encoder(conj_desc_erro)

fpGrowth = FPGrowth(transactions)
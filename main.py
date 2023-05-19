from database import DataBase
from fpgrowth import FPGrowth

db = DataBase.read_csv('test.csv', ';')

transactions = db.get_column('erros', key=lambda i: i.split(','))

fp_growth = FPGrowth(transactions, 0.4)

info = fp_growth.get_info()

print(info)
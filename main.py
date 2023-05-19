from database import DataBase
from fpgrowth import FPGrowth

import time

ini = time.time()

db = DataBase.read_csv('test.csv', ';')

conj_desc_erro = db.get_column('erros', key=lambda i: i.split(','))

transactions = DataBase.transaction_encoder(conj_desc_erro)

fp_growth = FPGrowth(transactions, 0.4)

end = time.time()

for frequent_itemset in fp_growth.frequent_itemsets:
    print(frequent_itemset, fp_growth.frequent_itemsets[frequent_itemset])

print(len(fp_growth.frequent_itemsets))


print(end - ini)
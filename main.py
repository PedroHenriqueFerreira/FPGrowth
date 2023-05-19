from database import DataBase
from fpgrowth import FPGrowth

import time

for support in [0.5, 0.4, 0.3, 0.2, 0.1, 0.05]:
    ini = time.time()

    db = DataBase.read_csv('test.csv', ';')

    conj_desc_erro = db.get_column('erros', key=lambda i: i.split(','))

    fp_growth = FPGrowth(conj_desc_erro, support)

    end = time.time()

    # for frequent_itemset in fp_growth.frequent_itemsets:
    #     print(frequent_itemset, fp_growth.frequent_itemsets[frequent_itemset])

    # print(len(fp_growth.frequent_itemsets))

    print(f'Para o suporte {support}:', end - ini)

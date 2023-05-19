import time

import pandas as pd

pd.set_option('display.max_rows', None)

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

ini = time.time()

data = pd.read_csv('test.csv', sep=';')
transations = [item.split(',') for item in data['erros'].dropna()]

transaction_encoder = TransactionEncoder()
transations_transformed = transaction_encoder.fit(transations).transform(transations)
transations_table = pd.DataFrame(transations_transformed, columns=transaction_encoder.columns_)

# print(transations_table)

frequent_itemsets = fpgrowth(transations_table, min_support=0.4, use_colnames=True)

end = time.time()

print(frequent_itemsets)

print(end - ini)

# result = association_rules(frequent_itemsets, metric='confidence', min_threshold=0.01)

# print(result)
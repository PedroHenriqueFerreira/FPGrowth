import pandas as pd

from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import fpgrowth, association_rules

data = pd.read_csv('teste.csv', sep=';')
transations = [item.split(',') for item in data['compras'].dropna()]

transaction_encoder = TransactionEncoder()
transations_transformed = transaction_encoder.fit(transations).transform(transations)
transations_table = pd.DataFrame(transations_transformed, columns=transaction_encoder.columns_)

print(transations_table)

frequent_itemsets = fpgrowth(transations_table, min_support=0.25, use_colnames=True)

print(frequent_itemsets)

result = association_rules(frequent_itemsets, metric='confidence', min_threshold=0.8)

print(result)
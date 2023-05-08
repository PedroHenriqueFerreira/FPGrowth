from typing import Any
from itertools import combinations

from database import DataBase

class FPTree:
    def __init__(self):
        self.root = FPNode()
        self.nodes: dict[str, list[FPNode]] = {}
        
    def insert_path(self, path: list[str]) -> None:
        node = self.root
        
        for item in path:
            if item not in node.children:
                node.children[item] = FPNode(item, node)
                
                if item not in self.nodes:
                    self.nodes[item] = [node.children[item]]
                else:
                    self.nodes[item].append(node.children[item])
                
            node.children[item].count += 1
            
            node = node.children[item]

class FPNode:
    def __init__(self, name: str | None = None, parent: Any | None = None):
        self.name = name
        self.parent = parent 
        
        self.children: dict[str, FPNode] = {}
        
        self.count = 0
        
        if self.parent is not None and name is not None:
            self.parent.children[name] = self

    def get_path(self):
        node = self
        
        path: list[str] = []
        
        while node.parent is not None and node.parent.name is not None:
            path.append(node.parent.name)
            
            node = node.parent
            
        return path

class FPGrowth:
    def __init__(self, transactions: DataBase, min_support: float = 0.5):
        self.transactions = transactions
        self.min_support = min_support
        
        self.get_item_support()
        
    def get_item_support(self):
        item_support: dict[str, float] = {column:0 for column in self.transactions.columns}
        support_per_item = 1 / len(self.transactions.data)
        
        for row in self.transactions.data:
            for i, item in enumerate(row):
                if not item:
                    continue
                    
                item_support[self.transactions.columns[i]] += support_per_item
            
        for column in item_support.copy():
            if item_support[column] >= self.min_support:
                continue
            
            del item_support[column]
        
        item_support = dict(sorted(item_support.items(), key=lambda i: i[1], reverse=True))
        
        fpTree = FPTree()
        
        for row in self.transactions.data:
            path = list(item_support.keys())
            
            for i, item in enumerate(row):
                if item:
                    continue
                
                column = self.transactions.columns[i]
                
                if column not in path:
                    continue
                    
                path.remove(column)
                    
            fpTree.insert_path(path)
        
        conditional_pattern: dict[str, dict[str, float]] = {}
            
        for column in reversed(item_support.keys()):
            nodes = fpTree.nodes[column]
            
            for node in nodes:
                path = node.get_path()
                
                for item in path:
                    if column not in conditional_pattern:
                        conditional_pattern[column] = {}
                    
                    if item not in conditional_pattern[column]:
                        conditional_pattern[column][item] = 0
                    
                    conditional_pattern[column][item] += node.count * support_per_item
            
            if column not in conditional_pattern:
                continue
            
            for item in list(conditional_pattern[column].keys()):
                if column not in conditional_pattern:
                    continue
                
                if conditional_pattern[column][item] >= self.min_support:
                    continue
                
                del conditional_pattern[column][item]
        
        frequent_itemsets: dict[tuple[str, ...], float] = {}
        
        for column in conditional_pattern:
            for i in range(2, len(conditional_pattern[column].keys()) + 2):
                values = list(combinations([column, *conditional_pattern[column].keys()], i))
                
                for value in values:
                    if column not in value:
                        continue
                    
                    support = []
                    
                    for item in value:
                        if item == column:
                            continue
                        
                        support.append(conditional_pattern[column][item])
                    
                    frequent_itemsets[value] = min(support)
        
        frequent_itemsets = dict(sorted(frequent_itemsets.items(), key=lambda i: i[1], reverse=True))
        
        for item in item_support:
            print(f'{item_support[item]:.2f}', item)
            
        for item in frequent_itemsets:
            print(f'{frequent_itemsets[item]:.2f}', item)
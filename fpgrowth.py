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
                    self.nodes[item] = []
                    
                self.nodes[item].append(node.children[item])
                
            node.children[item].count += 1
            
            node = node.children[item]

class FPNode:
    def __init__(self, name: str | None = None, parent: Any | None = None):
        self.name = name
        self.parent = parent 
        
        self.count = 0
        
        self.children: dict[str, FPNode] = {}
        
        if self.parent is not None and name is not None:
            self.parent.children[name] = self

    def get_path(self):
        path: list[str] = []
        
        node = self
        
        while node.parent is not None:
            if node.parent.name is None:
                break
            
            path.append(node.parent.name)
            
            node = node.parent
            
        return path

class FPGrowth:
    def __init__(self, transactions: DataBase, min_support: float = 0.5):
        self.transactions = transactions
        self.min_support = min_support
        
        self.item_support = 1 / len(transactions.data)
        
        self.frequent_items = self.get_frequent_items()
        
        self.fp_tree = FPTree()
        
        for row in self.transactions.data:
            items = [self.transactions.columns[i] for i, item in enumerate(row) if item]
            
            path = [frequent_item for frequent_item in self.frequent_items if frequent_item in items]
            
            self.fp_tree.insert_path(path)
        
        self.conditional_tree = self.get_conditional_tree()
        self.frequent_itemsets = self.get_frequent_itemsets()

        print(self.frequent_items)
        print(self.conditional_tree)
        
        for frequent_itemset in self.frequent_itemsets:
            print(frequent_itemset, self.frequent_itemsets[frequent_itemset])

        print(len(self.frequent_itemsets))

    def get_frequent_items(self):
        frequent_items: dict[str, float] = {}
        
        for row in self.transactions.data:
            for i, item in enumerate(row):
                if not item:
                    continue
                
                column = self.transactions.columns[i]
                
                if column not in frequent_items:
                    frequent_items[column] = 0
                    
                frequent_items[column] += self.item_support
    
        for frequent_item in frequent_items.copy():
            if frequent_items[frequent_item] >= self.min_support:
                continue
            
            del frequent_items[frequent_item]
            
        frequent_items = dict(sorted(frequent_items.items(), key=lambda i:i[1], reverse=True))
    
        return frequent_items
    
    def get_conditional_tree(self):
        conditional_tree: dict[str, dict[str, float]] = {}

        for frequent_item in reversed(self.frequent_items):
            nodes = self.fp_tree.nodes[frequent_item]
            
            for node in nodes:
                path = node.get_path()
                
                for item in path:
                    if frequent_item not in conditional_tree:
                        conditional_tree[frequent_item] = {}
                    
                    if item not in conditional_tree[frequent_item]:
                        conditional_tree[frequent_item][item] = 0
                    
                    conditional_tree[frequent_item][item] += node.count * self.item_support
            
            if frequent_item not in conditional_tree:
                continue
            
            for item in conditional_tree[frequent_item].copy():
                if conditional_tree[frequent_item][item] >= self.min_support:
                    continue
                
                del conditional_tree[frequent_item][item]
            
                
        return conditional_tree
    
    def get_frequent_itemsets(self):
        frequent_itemsets: dict[tuple[str, ...], float] = {}
        
        for conditional_item in self.conditional_tree:
            itemset = self.conditional_tree[conditional_item]
            
            for i in range(1, len(itemset) + 1):
                for combination in combinations(itemset, i):
                    support = min([itemset[item] for item in itemset if item in combination])
                    
                    frequent_itemsets[(conditional_item, *combination)] = support

        frequent_itemsets = dict(sorted(frequent_itemsets.items(), key=lambda i:i[1], reverse=True))

        return frequent_itemsets
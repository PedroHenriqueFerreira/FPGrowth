from math import ceil

from typing import Any
from itertools import combinations

from database import DataBase

class FPTree:
    def __init__(self, frequent_items: dict[str, int]):
        self.root = FPNode()
        
        self.nodes: dict[str, list[FPNode]] = {}
        self.conditional_items: list[str] = []
    
        self.frequent_items = frequent_items
    
    def is_path(self):
        if len(self.root.children) > 1:
            return False
        
        for node in self.nodes:
            if len(self.nodes[node]) > 1 or len(self.nodes[node][0].children) > 1:
                return False
            
        return True
    
    def conditional_tree(self, conditional_item: str, min_support: int) -> 'FPTree':
        paths: list[list[str]] = []
        
        parents_support: dict[str, int] = {}
        
        for node in self.nodes[conditional_item]:
            path = node.get_path()
            
            paths.append(path)
            
            for item in path:
                if item not in parents_support:
                    parents_support[item] = 0
                
                parents_support[item] += node.count
        
        for item in parents_support.copy():
            if parents_support[item] >= min_support:
                continue
                
            del parents_support[item]
        
        parents_support = dict(sorted(parents_support.items(), key=lambda i:i[1], reverse=True))

        fp_tree = FPTree(parents_support)
        
        for i, path in enumerate(paths):
            fp_tree.insert_path(path, self.nodes[conditional_item][i].count)
            
        fp_tree.conditional_items = [*self.conditional_items, conditional_item]
        
        return fp_tree
        
    def insert_path(self, path: list[str], count: int = 1) -> None:
        path = [item for item in self.frequent_items if item in path]
        
        node = self.root
        
        for item in path:
            if item not in node.children:
                node.children[item] = FPNode(item, node)
                
                if item not in self.nodes:
                    self.nodes[item] = []
                    
                self.nodes[item].append(node.children[item])
                
            node.children[item].count += count
            
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
        self.min_support = ceil(min_support * len(transactions.data))
    
        self.frequent_items = self.get_frequent_items()
    
        fp_tree = FPTree(self.frequent_items)
        
        for row in self.transactions.data:
            path = [self.transactions.columns[i] for i, item in enumerate(row) if item]
            
            fp_tree.insert_path(path)
        
        self.frequent_itemsets: dict[tuple[str, ...], float] = {}
        
        self.get_frequent_itemsets(fp_tree)

    def get_frequent_itemsets(self, fp_tree: FPTree) -> None:
        if fp_tree.is_path():
            for i in range(1, len(fp_tree.nodes) + 1):
                for itemset in combinations(fp_tree.nodes, i):
                    
                    support = min([fp_tree.nodes[item][0].count for item in itemset])
                    
                    self.frequent_itemsets[(*fp_tree.conditional_items, *itemset)] = support / len(self.transactions.data)
            return
        
        for node in fp_tree.nodes:
            support = sum([node.count for node in fp_tree.nodes[node]])
            
            self.frequent_itemsets[(*fp_tree.conditional_items, node)] = support / len(self.transactions.data)
            
            conditional_tree = fp_tree.conditional_tree(node, self.min_support)
            
            self.get_frequent_itemsets(conditional_tree)

    def get_frequent_items(self):
        frequent_items: dict[str, int] = {}
        
        for row in self.transactions.data:
            for i, item in enumerate(row):
                if not item:
                    continue
                
                column = self.transactions.columns[i]
                
                if column not in frequent_items:
                    frequent_items[column] = 0
                    
                frequent_items[column] += 1
    
        for frequent_item in frequent_items.copy():
            if frequent_items[frequent_item] >= self.min_support:
                continue
            
            del frequent_items[frequent_item]
            
        frequent_items = dict(sorted(frequent_items.items(), key=lambda i:i[1], reverse=True))
    
        return frequent_items
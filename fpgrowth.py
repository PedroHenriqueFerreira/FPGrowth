from math import ceil

from typing import Any
from itertools import combinations

from database import DataBase

class FPTree:
    def __init__(self, frequent_items: dict[str, int]):
        self.root = FPNode()
        
        self.frequent_items = frequent_items
        
        self.nodes: dict[str, list[FPNode]] = {}
        self.conditional_items: list[str] = []
    
    def has_single_path(self):
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
        
        parents_support = {k:parents_support[k] for k in parents_support if parents_support[k] >= min_support}
        parents_support = sorted(parents_support, key=parents_support.get, reverse=True) #type: ignore

        fp_tree = FPTree(parents_support)
        
        for i, path in enumerate(paths):
            fp_tree.insert_path(path, self.nodes[conditional_item][i].count)
        
        fp_tree.conditional_items.extend(self.conditional_items)
        fp_tree.conditional_items.append(conditional_item)
        
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
    
        fp_tree = FPTree(self.get_frequent_items())
        
        for row in self.transactions.data:
            path = [self.transactions.columns[i] for i, item in enumerate(row) if item]
            
            fp_tree.insert_path(path)
        
        self.frequent_itemsets: dict[tuple[str, ...], float] = {}
        
        self.generate_frequent_itemsets(fp_tree)

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
            
        frequent_items = {k:frequent_items[k] for k in frequent_items if frequent_items[k] >= self.min_support}
        frequent_items = sorted(frequent_items, key=frequent_items.get, reverse=True) # type: ignore
    
        return frequent_items

    def generate_frequent_itemsets(self, fp_tree: FPTree) -> None:
        if fp_tree.has_single_path():
            for i in range(1, len(fp_tree.nodes) + 1):
                for itemset in combinations(fp_tree.nodes, i):
                    support = min([fp_tree.nodes[item][0].count for item in itemset]) / len(self.transactions.data)
                    
                    self.frequent_itemsets[(*fp_tree.conditional_items, *itemset)] = support
            return
        
        for node in fp_tree.nodes:
            support = sum([node.count for node in fp_tree.nodes[node]]) / len(self.transactions.data)            
            
            self.frequent_itemsets[(*fp_tree.conditional_items, node)] = support 
            
            conditional_tree = fp_tree.conditional_tree(node, self.min_support)
            self.generate_frequent_itemsets(conditional_tree)
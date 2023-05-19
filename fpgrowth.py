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
    
    def conditional_tree(self, conditional_item: str, min_count: int) -> 'FPTree':
        paths: list[list[str]] = []
        
        parents_count: dict[str, int] = {}
        
        for node in self.nodes[conditional_item]:
            path = node.get_path()
            
            paths.append(path)
            
            for item in path:
                if item not in parents_count:
                    parents_count[item] = 0
                
                parents_count[item] += node.count
        
        parents_count = {k:parents_count[k] for k in parents_count if parents_count[k] >= min_count}
        parents_count = sorted(parents_count, key=parents_count.get, reverse=True) #type: ignore

        fp_tree = FPTree(parents_count)
        
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
    def __init__(self, transactions: list[list[str]], min_support: float = 0.5, decimal_precision: int = 6):
        self.transactions = transactions
        self.decimal_precision = decimal_precision
        
        self.min_count = ceil(min_support * len(transactions))
    
        fp_tree = FPTree(self.get_frequent_items())
        
        for row in self.transactions:
            fp_tree.insert_path(row)
        
        self.frequent_itemsets: dict[tuple[str, ...], float] = {}
        
        self.generate_frequent_itemsets(fp_tree)

    def get_frequent_items(self):
        frequent_items: dict[str, int] = {}
        
        for row in self.transactions:
            for item in row:
                if item not in frequent_items:
                    frequent_items[item] = 0
                    
                frequent_items[item] += 1
            
        frequent_items = {k:frequent_items[k] for k in frequent_items if frequent_items[k] >= self.min_count}
        frequent_items = sorted(frequent_items, key=frequent_items.get, reverse=True) # type: ignore
    
        return frequent_items

    def generate_frequent_itemsets(self, fp_tree: FPTree) -> None:
        if fp_tree.has_single_path():
            for i in range(1, len(fp_tree.nodes) + 1):
                for combination in combinations(fp_tree.nodes, i):
                    support = min([fp_tree.nodes[item][0].count for item in combination]) / len(self.transactions)
                    
                    itemset = tuple(sorted((*fp_tree.conditional_items, *combination)))
                    
                    self.frequent_itemsets[itemset] = round(support, self.decimal_precision)
            return
        
        for node in fp_tree.nodes:
            support = sum([node.count for node in fp_tree.nodes[node]]) / len(self.transactions)            
            
            itemset = tuple(sorted((*fp_tree.conditional_items, node)))
            
            self.frequent_itemsets[itemset] = round(support, self.decimal_precision)
            
            conditional_tree = fp_tree.conditional_tree(node, self.min_count)
            self.generate_frequent_itemsets(conditional_tree)
            
    def get_info(self):
        data: list[list[tuple[str, ...] | float]] = []
        
        for frequent_itemset in self.frequent_itemsets:
            if len(frequent_itemset) == 1:
                continue
            
            support = self.frequent_itemsets[frequent_itemset]
            
            for i in range(1, len(frequent_itemset)):
                for antecedent in combinations(frequent_itemset, i):
                    consequent = tuple(sorted(set(frequent_itemset) - set(antecedent)))
                    
                    antecedent_support = round(self.frequent_itemsets[antecedent], self.decimal_precision)
                    consequent_support = round(self.frequent_itemsets[consequent], self.decimal_precision)
                    
                    confidence = round(support / antecedent_support, self.decimal_precision)
                    conviction = round((1 - consequent_support) / (1 - confidence), self.decimal_precision)
                    lift = round(confidence / consequent_support, self.decimal_precision)
                    
                    data.append([
                        antecedent, 
                        consequent, 
                        antecedent_support, 
                        consequent_support, 
                        support, 
                        confidence, 
                        conviction, 
                        lift
                    ])  
            
        columns = [
            'antecedent', 
            'consequent', 
            'antecedent_support', 
            'consequent_support', 
            'support', 
            'confidence', 
            'conviction', 
            'lift'
        ]
            
        return DataBase(columns, data)
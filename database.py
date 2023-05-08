from typing import Any, Callable

class DataBase:
    def __init__(self, columns: list[str], data: list[list[Any]]):
        self.columns = columns
        self.data = data
        
    def get_column(self, column: str, key: Callable[[str], Any] = lambda i: i) -> list[Any]:
        index = self.columns.index(column)
        
        return [key(rows[index]) for rows in self.data if rows[index]]
        
    @staticmethod
    def read_csv(path: str, separator: str) -> 'DataBase':
        columns: list[str] = []
        data: list[list[Any]] = []
        
        with open(path, 'r', encoding='utf-8-sig') as f:
            for i, rows in enumerate(f.readlines()):
                values = rows.strip().split(separator)
                
                if i == 0:
                    columns = values
                else:
                    data.append(values)
                    
        return DataBase(columns, data)
    
    @staticmethod
    def transaction_encoder(data: list[list[str]]) -> 'DataBase':
        columns: set[str] = set()
        
        for rows in data:
            for item in rows:
                columns.add(item)
        
        columns_sorted = sorted(columns)
        columns_mapping = {v:i for i,v in enumerate(columns_sorted)}
        
        data_encoded = [[False for _ in columns_sorted] for _ in data]
        
        for i, rows in enumerate(data):
            for item in rows:
                data_encoded[i][columns_mapping[item]] = True
        
        return DataBase(columns_sorted, data_encoded)
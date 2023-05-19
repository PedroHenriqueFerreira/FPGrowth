from typing import Any, Callable, TypeVar

T = TypeVar('T')

class DataBase:
    def __init__(self, columns: list[str], data: list[list[Any]]):
        self.columns = columns
        self.data = data
    
    def __str__(self):
        return self.__repr__()
        
    def __repr__(self):
        columns_width = []
        
        for i in range(len(self.columns)):
            width = max([len(str(row[i])) for row in [self.columns, *self.data]])
            
            columns_width.append(width)
        
        lines = []
        
        for row in [self.columns, *self.data]:
            lines.append(' '.join([str(item).ljust(columns_width[i]) for i, item in enumerate(row)]))
            
        return '\n'.join(lines)
        
    def get_column(self, column: str, key: Callable[[str], T]) -> list[T]:
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
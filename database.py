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
            lines.append('  '.join([str(item).ljust(columns_width[i]) for i, item in enumerate(row)]))
            
        return '\n'.join(lines)
        
    def filter(self, columns: dict[str, Callable[[Any], bool]]):
        indexes = {self.columns.index(column): columns[column] for column in columns}
        
        data: list[list[Any]] = []
        
        for row in self.data:
            is_invalid = False
            
            for index in indexes:
                if not indexes[index](row[index]):
                    is_invalid = True
                    break
            
            if is_invalid:
                continue
            
            data.append(row)
            
        return DataBase(self.columns, data)
        
    
    def get_column_data(self, column: str, key: Callable[[str], T] = lambda i: i) -> list[T]: #type: ignore
        index = self.columns.index(column)
        
        return [key(rows[index]) for rows in self.data if rows[index]]
    
    def select_columns(self, columns: list[str]):
        indexes = [self.columns.index(column) for column in columns]
        
        data = []
        
        for row in self.data:            
            row = [row[index] for index in indexes]
            
            if len([item for item in row if not item]) > 0:
                continue
            
            data.append(row)
        
        return DataBase(columns, data)
    
    def group_by(self, column: str):
        index = self.columns.index(column)
        
        groups: dict[str, DataBase] = {}
        
        for row in self.data:
            if row[index] not in groups:
                groups[row[index]] = DataBase(self.columns, [])
                
            groups[row[index]].data.append(row)
            
        return groups
        
    @staticmethod
    def read_csv(path: str, separator: str = ',') -> 'DataBase':
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
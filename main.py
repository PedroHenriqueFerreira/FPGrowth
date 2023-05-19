from database import DataBase
from fpgrowth import FPGrowth

from utils import one_of, greater_than

groups = DataBase \
    .read_csv('SPAECE-MATEMATICA-LISTA-ACERTOS-ERROS-DISTRITO-TODOS.csv', ';') \
    .select_columns(['nm_turma', 'CONJ_DESC_ERRO']) \
    .filter({ 'nm_turma': one_of('9AAM-98', '9ABM-182') }) \
    .group_by('nm_turma')

for group in groups:
    transactions = groups[group].get_column_data('CONJ_DESC_ERRO', key=lambda i: i.split(','))
    
    associations = FPGrowth(transactions).get_associations()
    
    print(f'\nTurma: {group}\n')
    
    print(associations.filter({ 'lift': greater_than(1) }))
from database import DataBase
from fpgrowth import FPGrowth

db = DataBase.read_csv('SPAECE-MATEMATICA-LISTA-ACERTOS-ERROS-DISTRITO-TODOS.csv', ';')

db = db.select_columns(['nm_turma', 'CONJ_DESC_ERRO'])

db = db.filter({ 'nm_turma': '9AAT-98' })

transactions = db.get_column_data('CONJ_DESC_ERRO', key=lambda i: i.split(','))

associations = FPGrowth(transactions).get_associations()

print(associations.filter({ 'lift': (0, 2) }))
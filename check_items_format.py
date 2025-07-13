import sqlite3

conn = sqlite3.connect('pos_pedidos.db')
c = conn.cursor()

c.execute('SELECT id, items FROM pedidos WHERE estado = "pendiente" LIMIT 3')
rows = c.fetchall()

print('FORMATO DE ITEMS EN BD:')
for row in rows:
    print(f'ID: {row[0]}')
    print(f'Items: {repr(row[1])}')
    print('-' * 50)

conn.close()

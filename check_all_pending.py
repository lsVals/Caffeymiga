import sqlite3

conn = sqlite3.connect('pos_pedidos.db')
c = conn.cursor()

c.execute('SELECT id, items, total FROM pedidos WHERE estado = "pendiente" ORDER BY fecha_creacion DESC')
rows = c.fetchall()

print('TODOS LOS PEDIDOS PENDIENTES:')
for row in rows:
    print(f'ID: {row[0]}')
    print(f'Total: ${row[2]}')
    print(f'Items: {row[1][:200]}{"..." if len(row[1]) > 200 else ""}')
    print('-' * 60)

conn.close()

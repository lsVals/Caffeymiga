import sqlite3

conn = sqlite3.connect('pos_pedidos.db')
c = conn.cursor()

# Verificar pedidos totales
c.execute('SELECT COUNT(*) FROM pedidos')
total = c.fetchone()[0]
print(f'Total pedidos: {total}')

# Verificar pedidos pendientes
c.execute("SELECT COUNT(*) FROM pedidos WHERE estado='pendiente'")
pendientes = c.fetchone()[0]
print(f'Pedidos pendientes: {pendientes}')

# Mostrar algunos pedidos para verificar
c.execute("SELECT id, cliente_nombre, total, estado FROM pedidos LIMIT 5")
print("\nUltimos 5 pedidos:")
for row in c.fetchall():
    print(f"ID: {row[0]}, Cliente: {row[1]}, Total: ${row[2]:.2f}, Estado: {row[3]}")

conn.close()

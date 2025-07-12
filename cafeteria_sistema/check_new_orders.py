import sqlite3

conn = sqlite3.connect('pos_pedidos.db')
c = conn.cursor()

# Verificar pedidos pendientes
c.execute("SELECT COUNT(*) FROM pedidos WHERE estado='pendiente'")
pendientes = c.fetchone()[0]
print(f'Pedidos pendientes: {pendientes}')

# Mostrar últimos 3 pedidos
c.execute("SELECT id, cliente_nombre, total, estado, fecha_creacion FROM pedidos ORDER BY fecha_creacion DESC LIMIT 3")
print("\nÚltimos 3 pedidos:")
for row in c.fetchall():
    print(f"ID: {row[0][:20]}..., Cliente: {row[1]}, Total: ${row[2]:.2f}, Estado: {row[3]}, Fecha: {row[4]}")

conn.close()

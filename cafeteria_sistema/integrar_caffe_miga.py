#  INTEGRACIÓN AUTOMÁTICA CAFFE & MIGA
# Ejecutar UNA SOLA VEZ para agregar la integración a tu cafeteria_sistema.py

import os
import shutil
import re

def integrar_caffe_miga():
    print(" INTEGRANDO CAFFE & MIGA CON TU SISTEMA")
    print("=" * 50)
    
    # 1. Verificar archivos
    if not os.path.exists("cafeteria_sistema.py"):
        print(" No se encontró cafeteria_sistema.py")
        return False
    
    # 2. Hacer backup
    backup_name = "cafeteria_sistema_backup.py"
    shutil.copy2("cafeteria_sistema.py", backup_name)
    print(f" Backup creado: {backup_name}")
    
    # 3. Leer archivo original
    with open("cafeteria_sistema.py", "r", encoding="utf-8", errors="ignore") as f:
        contenido = f.read()
    
    # 4. Verificar si ya está integrado
    if "from caffe_miga_auto_integration import" in contenido:
        print(" ¡Ya está integrado! No se necesitan cambios.")
        return True
    
    # 5. Buscar donde agregar el import
    lineas = contenido.split('\n')
    import_agregado = False
    
    for i, linea in enumerate(lineas):
        if linea.startswith('import tkinter') and not import_agregado:
            lineas.insert(i + 1, "from caffe_miga_auto_integration import inicializar_caffe_miga, sincronizar_pedidos_web, iniciar_monitoreo_web")
            import_agregado = True
            break
    
    # 6. Buscar el __init__ de AppCafeteria y agregar la integración
    for i, linea in enumerate(lineas):
        if "class AppCafeteria" in linea:
            # Buscar el __init__ después de la clase
            for j in range(i, min(i + 50, len(lineas))):
                if "def __init__(self):" in lineas[j]:
                    # Buscar donde termina el __init__ (aproximadamente)
                    k = j + 1
                    while k < len(lineas) and (lineas[k].startswith('        ') or lineas[k].strip() == ''):
                        k += 1
                    
                    # Insertar la integración antes del final
                    lineas.insert(k - 1, "")
                    lineas.insert(k, "        #  INTEGRACIÓN CAFFE & MIGA")
                    lineas.insert(k + 1, "        try:")
                    lineas.insert(k + 2, "            inicializar_caffe_miga()")
                    lineas.insert(k + 3, "            iniciar_monitoreo_web()")
                    lineas.insert(k + 4, "            print(' Caffe & Miga integrado - Pedidos web automáticos')")
                    lineas.insert(k + 5, "        except Exception as e:")
                    lineas.insert(k + 6, "            print(f' Error Caffe & Miga: {e}')")
                    break
            break
    
    # 7. Guardar archivo modificado
    contenido_nuevo = '\n'.join(lineas)
    
    with open("cafeteria_sistema.py", "w", encoding="utf-8") as f:
        f.write(contenido_nuevo)
    
    print(" Integración completada!")
    print("\n RESULTADO:")
    print("    Los pedidos web aparecerán automáticamente")
    print("    Monitoreo cada 30 segundos")
    print("    Backup guardado como cafeteria_sistema_backup.py")
    
    return True

if __name__ == "__main__":
    print(" INTEGRADOR CAFFE & MIGA")
    print("Esto modificará tu cafeteria_sistema.py")
    
    respuesta = input("¿Continuar? (s/n): ").lower()
    
    if respuesta in ['s', 'si', 'y']:
        integrar_caffe_miga()
        print("\n ¡Ejecuta tu sistema normalmente!")
        print("   python cafeteria_sistema.py")
    else:
        print(" Cancelado")

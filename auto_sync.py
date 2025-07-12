#!/usr/bin/env python3
"""
Script de sincronización automática para Caffe & Miga
Ejecuta sincronización cada 60 segundos
"""

import time
import threading
import subprocess
import os
from datetime import datetime

class SincronizacionAutomatica:
    def __init__(self):
        self.running = False
        self.thread = None
        self.intervalo = 60  # segundos
        
    def iniciar(self):
        """Iniciar sincronización automática"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._loop_sincronizacion)
            self.thread.daemon = True
            self.thread.start()
            print("🚀 Sincronización automática iniciada")
            print(f"⏰ Intervalo: cada {self.intervalo} segundos")
            return True
        else:
            print("⚠️ La sincronización automática ya está ejecutándose")
            return False
    
    def detener(self):
        """Detener sincronización automática"""
        if self.running:
            self.running = False
            print("🛑 Sincronización automática detenida")
            return True
        else:
            print("ℹ️ La sincronización automática no estaba ejecutándose")
            return False
    
    def _loop_sincronizacion(self):
        """Loop principal de sincronización"""
        print("🔄 Loop de sincronización iniciado")
        
        while self.running:
            try:
                ahora = datetime.now().strftime("%H:%M:%S")
                print(f"\n[{ahora}] 🔄 Ejecutando sincronización...")
                
                # Ejecutar el script de sincronización
                resultado = subprocess.run(
                    ["python", "sincronizar_al_pos.py"],
                    capture_output=True,
                    text=True,
                    cwd=os.getcwd()
                )
                
                if resultado.returncode == 0:
                    # Extraer información relevante
                    output = resultado.stdout
                    if "Pedidos nuevos:" in output:
                        lines = output.split('\n')
                        for line in lines:
                            if "Pedidos nuevos:" in line or "Pedidos pendientes:" in line:
                                print(f"   {line.strip()}")
                    else:
                        print("   ✅ Sin cambios")
                else:
                    print(f"   ❌ Error en sincronización: {resultado.stderr}")
                
            except Exception as e:
                print(f"   ❌ Error ejecutando sincronización: {e}")
            
            # Esperar antes de la siguiente sincronización
            if self.running:
                time.sleep(self.intervalo)
        
        print("🏁 Loop de sincronización terminado")
    
    def cambiar_intervalo(self, nuevos_segundos):
        """Cambiar intervalo de sincronización"""
        self.intervalo = nuevos_segundos
        print(f"⏰ Intervalo cambiado a {nuevos_segundos} segundos")

def main():
    print("🏪 Sincronización Automática - Caffe & Miga")
    print("=" * 50)
    
    sync = SincronizacionAutomatica()
    
    print("💡 Comandos disponibles:")
    print("   'start' - Iniciar sincronización automática")
    print("   'stop'  - Detener sincronización")
    print("   'status' - Ver estado")
    print("   'interval X' - Cambiar intervalo a X segundos")
    print("   'exit'  - Salir del programa")
    print()
    
    try:
        while True:
            comando = input("🎛️ Comando: ").strip().lower()
            
            if comando == 'start':
                sync.iniciar()
                
            elif comando == 'stop':
                sync.detener()
                
            elif comando == 'status':
                estado = "🟢 EJECUTÁNDOSE" if sync.running else "🔴 DETENIDO"
                print(f"Estado: {estado}")
                print(f"Intervalo: {sync.intervalo} segundos")
                
            elif comando.startswith('interval'):
                try:
                    partes = comando.split()
                    if len(partes) == 2:
                        nuevos_segundos = int(partes[1])
                        if nuevos_segundos >= 10:
                            sync.cambiar_intervalo(nuevos_segundos)
                        else:
                            print("❌ El intervalo mínimo es 10 segundos")
                    else:
                        print("❌ Uso: interval <segundos>")
                except ValueError:
                    print("❌ Intervalo debe ser un número")
                    
            elif comando == 'exit':
                sync.detener()
                print("👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Comando no reconocido")
                
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo sincronización...")
        sync.detener()
        print("👋 ¡Hasta luego!")

if __name__ == "__main__":
    main()

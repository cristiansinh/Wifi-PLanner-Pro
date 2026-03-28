"""
WiFi Planner Pro v3.3 — PROFESSIONAL EDITION
=============================================
Sistema profesional de planificación WiFi con optimización extrema

CARACTERÍSTICAS v3.1:
- ✅ Soporte para PDF (carga directa sin conversión)
- ✅ Optimización multi-core para 50+ APs sin lag
- ✅ Herramientas avanzadas de dibujo de estructuras
- ✅ Sistema completo de proyectos (Nuevo/Guardar/Cargar)
- ✅ Rendering asíncrono con Web Workers
- ✅ Caché inteligente de cálculos

INSTALACIÓN:
    pip install pywebview pymupdf pillow psutil

EJECUTAR:
    python wifi_planner_v3.py

COMPILAR A .EXE:
    auto-py-to-exe
    O usar: compilar_v3.bat
"""

import webview
import sys
import os
import json
import base64
import gc
import threading
from pathlib import Path
from typing import Optional, Dict, Any
import time

# v3.3: Forzar UTF-8 en stdout/stderr para Windows (evita UnicodeEncodeError con emojis)
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Optimización de memoria
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.kernel32.SetProcessWorkingSetSize(-1, -1, -1)
    except:
        pass

# Intentar importar librerías opcionales
try:
    import fitz  # PyMuPDF para PDFs
    HAS_PDF = True
except ImportError:
    HAS_PDF = False
    print("⚠️  PyMuPDF no instalado - soporte PDF deshabilitado")
    print("   Instalar: pip install pymupdf")

try:
    from PIL import Image
    import io
    HAS_PIL = True
except ImportError:
    HAS_PIL = False
    print("⚠️  Pillow no instalado - optimización de imágenes deshabilitada")
    print("   Instalar: pip install pillow")

try:
    import psutil
    HAS_PSUTIL = True
except ImportError:
    HAS_PSUTIL = False
    print("⚠️  psutil no instalado - detección de recursos deshabilitada")


def resource_path(filename: str) -> str:
    """Obtiene la ruta correcta del recurso en .exe o desarrollo"""
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, filename)


class ProjectManager:
    """Gestor de proyectos con auto-guardado y respaldos"""
    
    def __init__(self):
        self.current_project_path: Optional[str] = None
        self.is_modified = False
        self.auto_save_enabled = True
        self.last_save_time = 0
        
    def mark_modified(self):
        """Marca el proyecto como modificado"""
        self.is_modified = True
        
    def mark_saved(self):
        """Marca el proyecto como guardado"""
        self.is_modified = False
        self.last_save_time = time.time()


class OptimizedAPIv3:
    """API optimizado v3.1 con soporte PDF y gestión avanzada"""
    
    def __init__(self, window_ref):
        self._window = window_ref
        self._cache = {}
        self.project_manager = ProjectManager()
        
        # Detectar recursos del sistema
        self.system_info = self._detect_system_resources()
        print(f"🖥️  Sistema: {self.system_info['cpu_count']} cores, "
              f"{self.system_info['memory_gb']:.1f}GB RAM")
    
    def _detect_system_resources(self) -> Dict[str, Any]:
        """Detecta recursos del sistema para optimización adaptativa"""
        info = {
            'cpu_count': os.cpu_count() or 2,
            'memory_gb': 4.0,  # default
            'platform': sys.platform
        }
        
        if HAS_PSUTIL:
            try:
                mem = psutil.virtual_memory()
                info['memory_gb'] = mem.total / (1024**3)
                info['memory_available_gb'] = mem.available / (1024**3)
            except:
                pass
        
        return info
    
    def get_system_info(self) -> Dict[str, Any]:
        """Retorna información del sistema para el frontend"""
        return self.system_info
    
    def open_plan_file(self) -> Optional[Dict[str, Any]]:
        """
        Abre plano - soporta imágenes Y PDFs
        Convierte PDFs a imágenes de alta calidad automáticamente
        """
        try:
            file_types = [
                'Archivos soportados (*.pdf;*.png;*.jpg;*.jpeg;*.bmp)',
                'PDF (*.pdf)',
                'Imágenes (*.png;*.jpg;*.jpeg;*.bmp)',
                'Todos los archivos (*.*)'
            ]
            
            result = self._window.create_file_dialog(
                webview.OPEN_DIALOG,
                allow_multiple=False,
                file_types=tuple(file_types)
            )
            
            if not result or len(result) == 0:
                return None
            
            filepath = result[0]
            file_ext = os.path.splitext(filepath)[1].lower()
            
            # Validar tamaño
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            if file_size_mb > 100:
                return {
                    'error': f'Archivo muy grande: {file_size_mb:.1f}MB (máx 100MB)'
                }
            
            # Procesar según tipo
            if file_ext == '.pdf':
                return self._process_pdf(filepath)
            else:
                return self._process_image(filepath)
                
        except Exception as e:
            return {'error': f'Error al abrir archivo: {str(e)}'}
    
    def _process_pdf(self, filepath: str) -> Dict[str, Any]:
        """Convierte PDF a imagen de alta calidad"""
        if not HAS_PDF:
            return {
                'error': 'Soporte PDF no disponible. Instalar: pip install pymupdf'
            }
        
        try:
            print(f"📄 Procesando PDF: {os.path.basename(filepath)}")
            
            # Abrir PDF
            doc = fitz.open(filepath)
            
            if len(doc) == 0:
                return {'error': 'PDF vacío o corrupto'}
            
            # Usar primera página
            page = doc[0]
            
            # Calcular zoom para buena calidad (300 DPI equivalente)
            # zoom = 300 / 72 = 4.166
            zoom = 4.0
            mat = fitz.Matrix(zoom, zoom)
            
            # Renderizar a imagen
            pix = page.get_pixmap(matrix=mat, alpha=False)
            
            # Convertir a PNG
            img_data = pix.tobytes("png")
            
            # Optimizar si PIL disponible
            if HAS_PIL:
                img = Image.open(io.BytesIO(img_data))
                
                # Si es muy grande, redimensionar manteniendo aspecto
                max_dimension = 4096
                if max(img.size) > max_dimension:
                    ratio = max_dimension / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    print(f"  📐 Redimensionado a {new_size[0]}x{new_size[1]}")
                
                # Convertir a bytes
                buffer = io.BytesIO()
                img.save(buffer, format='PNG', optimize=True)
                img_data = buffer.getvalue()
            
            doc.close()
            
            # Encodear a base64
            b64_data = base64.b64encode(img_data).decode('utf-8')
            
            # Limpiar memoria
            del img_data
            gc.collect()
            
            print(f"  ✅ PDF convertido - Tamaño: {len(b64_data)/1024:.0f}KB")
            
            return {
                'data': f'data:image/png;base64,{b64_data}',
                'name': os.path.basename(filepath),
                'size': len(b64_data) / 1024,  # KB
                'type': 'pdf',
                'original_path': filepath
            }
            
        except Exception as e:
            return {'error': f'Error al procesar PDF: {str(e)}'}
    
    def _process_image(self, filepath: str) -> Dict[str, Any]:
        """Procesa y optimiza imagen"""
        try:
            print(f"🖼️  Procesando imagen: {os.path.basename(filepath)}")
            
            # Leer archivo
            with open(filepath, 'rb') as f:
                img_data = f.read()
            
            # Optimizar con PIL si disponible
            if HAS_PIL:
                img = Image.open(io.BytesIO(img_data))
                
                # Convertir a RGB si es necesario
                if img.mode not in ('RGB', 'RGBA'):
                    img = img.convert('RGB')
                
                # Redimensionar si es muy grande
                max_dimension = 4096
                if max(img.size) > max_dimension:
                    ratio = max_dimension / max(img.size)
                    new_size = tuple(int(dim * ratio) for dim in img.size)
                    img = img.resize(new_size, Image.Resampling.LANCZOS)
                    print(f"  📐 Redimensionado a {new_size[0]}x{new_size[1]}")
                
                # Re-encodear optimizado
                buffer = io.BytesIO()
                img.save(buffer, format='PNG', optimize=True)
                img_data = buffer.getvalue()
            
            # Base64
            b64_data = base64.b64encode(img_data).decode('utf-8')
            
            # Detectar MIME
            ext = os.path.splitext(filepath)[1].lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.bmp': 'image/bmp'
            }
            mime = mime_types.get(ext, 'image/png')
            
            # Limpiar
            del img_data
            gc.collect()
            
            print(f"  ✅ Imagen procesada - Tamaño: {len(b64_data)/1024:.0f}KB")
            
            return {
                'data': f'data:{mime};base64,{b64_data}',
                'name': os.path.basename(filepath),
                'size': len(b64_data) / 1024,
                'type': 'image',
                'original_path': filepath
            }
            
        except Exception as e:
            return {'error': f'Error al procesar imagen: {str(e)}'}
    
    def new_project(self) -> Dict[str, Any]:
        """Crea un nuevo proyecto"""
        try:
            # Si hay proyecto actual modificado, confirmar
            if self.project_manager.is_modified:
                # El frontend debe manejar la confirmación
                pass
            
            # Reset project manager
            self.project_manager.current_project_path = None
            self.project_manager.is_modified = False
            
            return {'success': True, 'message': 'Nuevo proyecto creado'}
            
        except Exception as e:
            return {'error': str(e)}
    
    def save_project(self, json_str: str, save_as: bool = False) -> Dict[str, Any]:
        """
        Guarda proyecto
        save_as=True: siempre pide ubicación nueva
        save_as=False: guarda en ubicación actual o pide si es nuevo
        """
        try:
            # Determinar ruta
            if save_as or self.project_manager.current_project_path is None:
                # Pedir ubicación
                result = self._window.create_file_dialog(
                    webview.SAVE_DIALOG,
                    save_filename='proyecto_wifi.wfp',
                    file_types=(
                        'WiFi Planner Project (*.wfp)',
                        'JSON (*.json)',
                        'Todos los archivos (*.*)'
                    )
                )
                
                if not result:
                    return {'cancelled': True}
                
                filepath = result if isinstance(result, str) else result[0]
            else:
                # Guardar en ubicación actual
                filepath = self.project_manager.current_project_path
            
            # Asegurar extensión
            if not filepath.lower().endswith(('.wfp', '.json')):
                filepath += '.wfp'
            
            # Guardar archivo
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(json_str)
            
            # Backup automático
            backup_path = filepath.replace('.wfp', '_backup.wfp').replace('.json', '_backup.json')
            try:
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(json_str)
            except:
                pass  # Backup opcional
            
            # Actualizar project manager
            self.project_manager.current_project_path = filepath
            self.project_manager.mark_saved()
            
            print(f"💾 Proyecto guardado: {os.path.basename(filepath)}")
            
            return {
                'success': True,
                'path': filepath,
                'filename': os.path.basename(filepath)
            }
            
        except Exception as e:
            return {'error': f'Error al guardar: {str(e)}'}
    
    def save_project_as(self, json_str: str) -> Dict[str, Any]:
        """Guardar proyecto como (siempre pide ubicación)"""
        return self.save_project(json_str, save_as=True)
    
    def load_project(self) -> Optional[Dict[str, Any]]:
        """Carga proyecto desde archivo"""
        try:
            result = self._window.create_file_dialog(
                webview.OPEN_DIALOG,
                allow_multiple=False,
                file_types=(
                    'WiFi Planner Project (*.wfp;*.json)',
                    'Todos los archivos (*.*)'
                )
            )
            
            if not result or len(result) == 0:
                return None
            
            filepath = result[0]
            
            # Validar tamaño
            file_size_mb = os.path.getsize(filepath) / (1024 * 1024)
            if file_size_mb > 200:
                return {'error': f'Proyecto muy grande: {file_size_mb:.1f}MB'}
            
            # Leer archivo
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Validar JSON
            try:
                json.loads(content)
            except json.JSONDecodeError as e:
                return {'error': f'Archivo JSON corrupto: {str(e)}'}
            
            # Actualizar project manager
            self.project_manager.current_project_path = filepath
            self.project_manager.mark_saved()
            
            print(f"📂 Proyecto cargado: {os.path.basename(filepath)}")
            
            return {
                'data': content,
                'path': filepath,
                'filename': os.path.basename(filepath)
            }
            
        except Exception as e:
            return {'error': f'Error al cargar: {str(e)}'}
    
    def export_png(self, data_url: str) -> Dict[str, Any]:
        """Exporta heatmap a PNG"""
        try:
            result = self._window.create_file_dialog(
                webview.SAVE_DIALOG,
                save_filename='wifi_heatmap.png',
                file_types=(
                    'PNG Image (*.png)',
                    'Todos los archivos (*.*)'
                )
            )
            
            if not result:
                return {'cancelled': True}
            
            filepath = result if isinstance(result, str) else result[0]
            
            # Asegurar extensión
            if not filepath.lower().endswith('.png'):
                filepath += '.png'
            
            # Decodificar y guardar
            header, encoded = data_url.split(',', 1)
            with open(filepath, 'wb') as f:
                f.write(base64.b64decode(encoded))
            
            print(f"📥 PNG exportado: {os.path.basename(filepath)}")
            
            return {
                'success': True,
                'path': filepath,
                'filename': os.path.basename(filepath)
            }
            
        except Exception as e:
            return {'error': f'Error al exportar: {str(e)}'}
    
    def mark_project_modified(self) -> None:
        """Marca proyecto como modificado (llamado desde JS)"""
        self.project_manager.mark_modified()


def main():
    """Función principal"""
    
    print("=" * 60)
    print("WiFi Planner Pro v3.3 — PROFESSIONAL EDITION")
    print("=" * 60)
    print()
    
    # Verificar dependencias
    print("📦 Verificando dependencias:")
    print(f"  ✅ pywebview")
    print(f"  {'✅' if HAS_PDF else '❌'} pymupdf (PDF support)")
    print(f"  {'✅' if HAS_PIL else '❌'} Pillow (image optimization)")
    print(f"  {'✅' if HAS_PSUTIL else '❌'} psutil (system detection)")
    print()
    
    # Buscar HTML
    html_path = resource_path('wifi_planner_v3.html')
    
    if not os.path.exists(html_path):
        print(f"❌ ERROR: No se encontró {html_path}")
        print(f"   Buscando en: {os.path.dirname(html_path)}")
        input("Presiona Enter para salir...")
        sys.exit(1)
    
    print(f"✅ Interfaz encontrada: {os.path.basename(html_path)}")
    print()
    
    # Crear ventana
    window = webview.create_window(
        title='WiFi Planner Pro v3.3 — Professional Edition',
        url=html_path,
        width=1700,
        height=1000,
        min_size=(1400, 800),
        resizable=True,
        confirm_close=True,
        background_color='#08090d',
        text_select=False,
    )
    
    # Crear y exponer API
    api = OptimizedAPIv3(window)
    
    window.expose(
        api.get_system_info,
        api.open_plan_file,
        api.new_project,
        api.save_project,
        api.save_project_as,
        api.load_project,
        api.export_png,
        api.mark_project_modified
    )
    
    print("🚀 Iniciando aplicación...")
    print()
    
    # Iniciar
    webview.start(
        debug=False,
        http_server=True,
        gui='edgechromium' if sys.platform == 'win32' else None
    )
    
    # Limpieza
    print()
    print("👋 Cerrando aplicación...")
    gc.collect()


if __name__ == '__main__':
    # Optimizaciones de inicio
    gc.set_threshold(700, 10, 10)
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n⚠️  Interrumpido por usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ ERROR CRÍTICO: {e}")
        import traceback
        traceback.print_exc()
        input("\nPresiona Enter para salir...")
        sys.exit(1)


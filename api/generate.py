from http.server import BaseHTTPRequestHandler
import json
import base64
from io import BytesIO
import sys

# Instalar openpyxl si no está
try:
    from openpyxl import load_workbook
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "openpyxl", "-t", "/tmp/"])
    sys.path.insert(0, "/tmp/")
    from openpyxl import load_workbook


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        try:
            # Leer datos
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            # Obtener plantilla y CSV en base64
            plantilla_b64 = data.get('plantilla')
            ordenes = data.get('ordenes', [])
            
            if not plantilla_b64:
                self.send_error_response('Falta la plantilla')
                return
            
            if not ordenes:
                self.send_error_response('No hay órdenes')
                return
            
            # Decodificar plantilla
            plantilla_bytes = base64.b64decode(plantilla_b64)
            plantilla_io = BytesIO(plantilla_bytes)
            
            # Cargar workbook
            wb = load_workbook(plantilla_io)
            ws = wb['A domicilio']
            
            # Escribir datos desde fila 3
            for idx, o in enumerate(ordenes):
                row = idx + 3
                ws.cell(row=row, column=1, value='')  # Paquete Guardado
                ws.cell(row=row, column=2, value=int(o.get('peso', 10001)))
                ws.cell(row=row, column=3, value=int(o.get('alto', 10)))
                ws.cell(row=row, column=4, value=int(o.get('ancho', 10)))
                ws.cell(row=row, column=5, value=int(o.get('prof', 10)))
                ws.cell(row=row, column=6, value=int(o.get('valor', 0)))
                ws.cell(row=row, column=7, value=o.get('numeroInterno', ''))
                ws.cell(row=row, column=8, value=o.get('nombre', ''))
                ws.cell(row=row, column=9, value=o.get('apellido', ''))
                ws.cell(row=row, column=10, value=str(o.get('dni', '')))
                ws.cell(row=row, column=11, value=o.get('email', ''))
                ws.cell(row=row, column=12, value=str(o.get('celCodigo', '')))
                ws.cell(row=row, column=13, value=str(o.get('celNumero', '')))
                ws.cell(row=row, column=14, value=o.get('calle', ''))
                ws.cell(row=row, column=15, value=str(o.get('numero', '')))
                ws.cell(row=row, column=16, value=str(o.get('piso', '') or ''))
                ws.cell(row=row, column=17, value=str(o.get('depto', '') or ''))
                ws.cell(row=row, column=18, value=o.get('ubicacion', ''))
                ws.cell(row=row, column=19, value=o.get('observaciones', '') or '')
            
            # Guardar en memoria
            output = BytesIO()
            wb.save(output)
            output.seek(0)
            
            # Convertir a base64 para enviar
            excel_b64 = base64.b64encode(output.read()).decode('utf-8')
            
            # Enviar respuesta
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({
                'success': True,
                'excel': excel_b64,
                'count': len(ordenes)
            }).encode())
            
        except Exception as e:
            self.send_error_response(str(e))
    
    def send_error_response(self, message):
        self.send_response(400)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps({'error': message}).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

from django.db import models
#
from django.contrib.auth.models import BaseUserManager
from django.db.models import Q, F
import qrcode
import io
import os
from django.conf import settings

import base64
from PIL import Image, UnidentifiedImageError
import win32print
import win32api
from django.core.files.storage import FileSystemStorage
class ProductoManager(BaseUserManager, models.Manager):
    def productos_activos(self):
        return self.filter(
            anulate=False
        )
    def productos_en_cero(self):
        #
        consulta = self.filter(
           count__lt=10
        )
        #
        return consulta
    def buscar_producto(self, kword, order):
        consulta = self.filter(
            Q(name__icontains=kword) | Q(codigo=kword)
        )
        # verificamos en que orden se solicita
        if order == 'date':
            # ordenar por fecha
            return consulta.order_by('created')
        elif order == 'name':
            # ordenar por nombre
            return consulta.order_by('name')
        elif order == 'stok':
            return consulta.order_by('count')
        else:
            return consulta.order_by('-created')
        
    def generate_qr_codes(self, producto, count):
        qr_codes = []
        
        # Definir la ruta donde se guardarán los QR
        qr_directory = os.path.join(settings.MEDIA_ROOT, 'img_qr')
        
        # Crear la carpeta si no existe
        if not os.path.exists(qr_directory):
            os.makedirs(qr_directory)
        
        # Generar el QR para el producto
        qr_data = f'Prd:{producto.id}'  # El código QR será único por producto
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=0,
        )
        qr.add_data(qr_data)
        qr.make(fit=True)
        qr_img = qr.make_image(fill="black", back_color="white")

        # Guardar la imagen en un archivo temporal
        buffered = io.BytesIO()
        qr_img.save(buffered, format="PNG")
        buffered.seek(0)

        # Definir el nombre del archivo para el QR
        qr_file_name = f'qr_{producto.codigo}.png'
        qr_file_path = os.path.join(qr_directory, qr_file_name)
        # Verificar si el archivo ya existe y eliminarlo
        if os.path.exists(qr_file_path):
            os.remove(qr_file_path) 
        # Guardar el archivo en el directorio img_qr
        fs = FileSystemStorage(location=qr_directory)
        fs.save(qr_file_name, buffered)

        # Retornar la ruta del archivo guardado
        qr_codes.append(qr_file_path)

        return qr_codes
    
    def print_qr_codes(self, qr_codes, count):
        # Crear una imagen para imprimir todos los códigos QR juntos
        images = []
        
        # Asegurarse de que el count no sea mayor que el número de códigos QR disponibles
        for qr_file in qr_codes * count:  # Multiplicamos los QR por el count
            try:
                # Abrir la imagen QR desde la ruta
                qr_img = Image.open(qr_file).convert('RGB')
                qr_img = qr_img.resize((200, 200))  # Ajustar tamaño del QR a 200 px x 200 px
                images.append(qr_img)
            except Exception as e:
                print(f"Error al procesar el código QR: {e}")
                continue  # Ignorar el código QR defectuoso y continuar con los demás

        if images:
            num_per_row = 5  # Número de códigos QR por fila
            spacing = 15  # Espacio entre códigos QR en píxeles
            total_width = num_per_row * 200 + (num_per_row - 1) * spacing  # Ajustar para espacio entre QR
            num_rows = (len(images) + num_per_row - 1) // num_per_row
            total_height = num_rows * 200 + (num_rows - 1) * spacing  # Ajustar para espacio entre QR
            
            combined_img = Image.new('RGB', (total_width, total_height), 'white')
            y_offset = 0
            x_offset = 0

            for i, img in enumerate(images):
                combined_img.paste(img, (x_offset, y_offset))
                x_offset += 200 + spacing  # 200 px para QR + espacio
                if (i + 1) % num_per_row == 0:
                    x_offset = 0
                    y_offset += 200 + spacing  # 200 px para QR + espacio
            
            # Ajustar la imagen a 7 cm de ancho con 450 PPI
            width_cm = 7
            width_inches = width_cm / 2.54
            width_pixels = int(width_inches * 450)
            height_pixels = int(total_height * (width_pixels / total_width))
            
            combined_img = combined_img.resize((width_pixels, height_pixels), Image.LANCZOS)
            
            # Guardar la imagen combinada en la carpeta qr_print dentro de media
            media_dir = os.path.join(settings.MEDIA_ROOT, 'qr_print')
            if not os.path.exists(media_dir):
                os.makedirs(media_dir)
            combined_image_path = os.path.join(media_dir, "combined_qr_codes.png")
            combined_img.save(combined_image_path, dpi=(450, 450))

            return combined_image_path  
    

    
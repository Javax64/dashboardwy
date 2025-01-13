from django.db import models
from django.conf import settings
from django.db.models.signals import pre_delete, post_save
#
from model_utils.models import TimeStampedModel

# local apps
from applications.productos.models import Producto
from .signals import update_stok_ventas_producto
#
from .managers import SaleManager, SaleDetailManager, CarShopManager
# Create your models here.
class Sale(TimeStampedModel):
    """Modelo que representa a una Venta Global"""

    # tipo recibo constantes
    BOLETA = '0'
    FACTURA = '1'
    SIN_COMPROBANTE = '2'
    # tipo pago constantes
    TRANSFERENCIA = '0'
    EFECTVO = '1'
    OTRO = '3'
    #
    TIPO_INVOCE_CHOICES = [
        (BOLETA, 'Boleta'),
        (FACTURA, 'Factura'),
        (SIN_COMPROBANTE, 'Sin Comprobante'),
    ]

    TIPO_PAYMENT_CHOICES = [
        (TRANSFERENCIA, 'Transferencia'),
        (EFECTVO, 'Efectivo'),
        
    ]

    date_sale = models.DateTimeField(
        'Fecha de Venta',
    )
    count = models.PositiveIntegerField('Cantidad de Productos')
    amount = models.DecimalField(
        'Monto', 
        max_digits=10, 
        decimal_places=2
    )
    type_invoce = models.CharField(
        'TIPO',
        max_length=2,
        choices=TIPO_INVOCE_CHOICES
    )
    type_payment = models.CharField(
        'TIPO PAGO',
        max_length=2,
        choices=TIPO_PAYMENT_CHOICES
    )
    descuento = models.DecimalField(
        'Descuento', 
        max_digits=10, 
        decimal_places=2
    )
    
    close = models.BooleanField(
        'Venta cerrada',
        default=False
    )
    
    anulate = models.BooleanField(
        'Venta Anulada',
        default=False,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='cajero',
        related_name="user_venta",
    )

    objects = SaleManager()

    class Meta:
        verbose_name = 'Venta'
        verbose_name_plural = 'ventas'

    def __str__(self):
        return 'Nº [' + str(self.id) + '] - ' + str(self.date_sale)

class SaleDetail(TimeStampedModel):
    """Modelo que representa a una venta en detalle"""

    product = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        verbose_name='producto',
        related_name='product_sale'
    )
    sale = models.ForeignKey(
        Sale,
        on_delete=models.CASCADE, 
        verbose_name='Codigo de Venta',
        related_name='detail_sale'
    )
    count = models.PositiveIntegerField('Cantidad')
    
    price_sale = models.DecimalField(
        'Precio Venta', 
        max_digits=10, 
        decimal_places=2
    )
    tax = models.DecimalField(
        'Impuesto antes tax', 
        max_digits=5,
        decimal_places=2
    )
    anulate = models.BooleanField(default=False)
    #

    objects = SaleDetailManager()

    class Meta:
        verbose_name = 'Producto Vendido'
        verbose_name_plural = 'Productos vendidos'

    def __str__(self):
        return str(self.sale.id) + ' - ' + str(self.product.name)



class Cart(TimeStampedModel):
    """Modelo que representa un carrito de compras"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Usuario',
        related_name='user_cart',
        default=1
    )
    is_active = models.BooleanField(default=True, verbose_name='Carrito activo')
    
    

    class Meta:
        verbose_name = 'Carrito de compras'
        verbose_name_plural = 'Carritos de compras'
        ordering = ['-created']

    def __str__(self):
        return f"Carrito de {self.user.username}"
    

class CarShop(TimeStampedModel):
    """Modelo que representa a un carrito de compras"""
    #user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=1)
    
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name='Carrito',
        blank=True,
        null=True,
        default=1
    )
    
    barcode = models.CharField(
        max_length=13,
        unique=False
    )
    product = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        verbose_name='producto',
        related_name='product_car'
    )
    count = models.PositiveIntegerField('Cantidad')
    
    objects = CarShopManager()

    class Meta:
        verbose_name = 'productos del Carrito de compras'
        verbose_name_plural = 'productos del Carrito de compras'
        ordering = ['-created']
        

    def __str__(self):
        return str(self.product.name)
# signals for venta
post_save.connect(update_stok_ventas_producto, sender=SaleDetail)

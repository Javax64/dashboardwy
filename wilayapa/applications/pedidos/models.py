from django.db import models
from model_utils.models import TimeStampedModel
from django.conf import settings
# local apps
from applications.productos.models import Producto, Extra

#
from .managers import PedidoManager, PedidoDetailManager, CarShopPManager


# Create your models here.
class Pedido(TimeStampedModel):
    """Modelo que representa a una Venta Global"""

    # tipo recibo constantes
    BOLETA = '0'
    FACTURA = '1'
    SIN_COMPROBANTE = '2'
    # tipo de entrega
    TIENDA = '0'
    ENVIO = '1'
    DELIVERY = '2'
    # tipo pago constantes
    TRANSFERENCIA = '0'
    EFECTVO = '1'
    # tipo pago constantes saldo
    TRANSFERENCIA_S = '0'
    EFECTVO_S = '1'
    
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
    TIPO_PAYMENT_CHOICES_SALDO = [
        (TRANSFERENCIA_S, 'Transferencia'),
        (EFECTVO_S, 'Efectivo'),
        
    ]
    METODO_DE_ENTREGA = [
        (TIENDA, 'Entrega en Tienda'),
        (ENVIO, 'Envio'),
        (DELIVERY, 'Delivery'),
        
    ]

    date_sale = models.DateTimeField(
        'Fecha de pedido',
    )
    date_entrega = models.DateTimeField(
        'Fecha de entrega',
    )
    cliente_nombre = models.CharField(
        'Nombre del cliente', 
        max_length=50,
        
    )
    cliente_celular = models.CharField(
        'Celular del cliente', 
        max_length=50,
        
    )
    count = models.PositiveIntegerField('Cantidad de Productos')
    amount = models.DecimalField(
        'Monto', 
        max_digits=10, 
        decimal_places=2
    )
    adelanto = models.DecimalField(
        'ADELANTO', 
        max_digits=20, 
        decimal_places=2,
        blank=True,
        default=0,
    )
    type_payment = models.CharField(
        'TIPO PAGO ADELANTO',
        max_length=2,
        choices=TIPO_PAYMENT_CHOICES
    )
    saldo = models.DecimalField(
        'SALDO', 
        max_digits=20, 
        decimal_places=2,
        default=0,
        null=True, 
        blank=True,
    )
    type_payment_saldo = models.CharField(
        'TIPO PAGO SALDO',
        max_length=2,
        choices=TIPO_PAYMENT_CHOICES_SALDO,
        blank=True,
    )
    
    descuento = models.DecimalField(
        'DESCUENTO', 
        max_digits=10, 
        decimal_places=2,
        blank=True,
        default=0,
    )
    
    
    
    type_entrega = models.CharField(
        'METODO DE ENTREGA',
        max_length=2,
        default=0,
        choices=METODO_DE_ENTREGA
    )
    
    
    
    
    
    cliente_carnet = models.CharField(
        'carnet del cliente', 
        max_length=50,
        blank=True,
        
    )
    
    
    cliente_departamento = models.CharField(
        'departamento del cliente', 
        max_length=50,
        blank=True,
        
    )
    cliente_direccion = models.CharField(
        'direccion de delivery',
        max_length= 70,
        blank=True,
    )
    cliente_sucursal = models.CharField(
        'sucursal de envio del cliente',
        max_length=50,
        blank=True,
    )
    description = models.TextField(
        'descripcion del pedido',
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Admin Pedido',
        related_name="user_pedido",
    )
    entregado = models.BooleanField(
        'Pedido entregado',
        default=False,
    )
    
    anulate = models.BooleanField(
        'Pedido Anulado',
        default=False,
    )

    type_invoce = models.CharField(
        'TIPO',
        max_length=2,
        default=0,
        choices=TIPO_INVOCE_CHOICES
    )
    
  
    objects = PedidoManager()

    class Meta:
        verbose_name = 'Peido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return 'Nº [' + str(self.id) + '] - ' + str(self.date_sale)



class PedidoDetail(TimeStampedModel):
    """Modelo que representa a un Pedido en detalle"""

    product = models.ForeignKey(
        Producto,
        on_delete=models.CASCADE,
        verbose_name='producto',
        related_name='product_pedido'
    )
    pedido = models.ForeignKey(
        Pedido,
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
        'Impuesto', 
        max_digits=5,
        decimal_places=2
    )
    anulate = models.BooleanField(default=False)
    entregado = models.BooleanField(
        'Pedido entregado',
        default=False
    )
    #
    # Relación Many-to-Many con los extras
    extras = models.ManyToManyField(
        Extra, 
        blank=True, 
        related_name='pedido_details',
        verbose_name='Extras'
    )
    objects = PedidoDetailManager()

    class Meta:
        verbose_name = 'Producto Vendido'
        verbose_name_plural = 'Productos vendidos'

    def __str__(self):
        return str(self.pedido.id) + ' - ' + str(self.product.name)

class CartP(TimeStampedModel):
    """Modelo que representa un carrito de compras"""
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Usuario',
        related_name='user_cart_ped',
        default=1
    )
    is_active = models.BooleanField(default=True, verbose_name='Carrito activo')
    
    productos_cargados = models.BooleanField(default=False, verbose_name='Productos cargados al carrito')

    class Meta:
        verbose_name = 'Cart Pedido'
        verbose_name_plural = 'Cart Pedidos'
        ordering = ['-created']

    def __str__(self):
        return f"Carrito de {self.user.username}"
    
class CarShopPed(TimeStampedModel):
    """Modelo que representa a un carrito de compras"""
    cart = models.ForeignKey(
        CartP,
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
        related_name='product_car_ped'
    )
    extras = models.ManyToManyField(Extra, blank=True)
    count = models.PositiveIntegerField('Cantidad')
    # Nuevo campo para almacenar el precio total con extras
    precio_total = models.DecimalField(
        'Precio Total',
        max_digits=10,
        decimal_places=2,
        default=0
    )

    objects = CarShopPManager()

    class Meta:
        verbose_name = 'CartShop Pedido'
        verbose_name_plural = 'CartShop Pedidos'
        ordering = ['-created']

    def __str__(self):
        return str(self.product.name)

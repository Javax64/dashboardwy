from django.db import models

# Create your models here.

from model_utils.models import TimeStampedModel
from django.db import models
from .managers import ProductoManager

class Marca(TimeStampedModel):
    """
        Marca de un producto
    """

    name = models.CharField(
        'Nombre', 
        max_length=30
    )

    class Meta:
        verbose_name = 'Marca'
        verbose_name_plural = 'Marcas'

    def __str__(self):
        return self.name


    
class Extra(TimeStampedModel):
    """
        Extras de Producto
    """

    name = models.CharField(
        'Nombre Extra', 
        max_length=30
    )
    price = models.DecimalField(
        'precio venta',
        max_digits=7, 
        decimal_places=2
    )
    activate = models.BooleanField(
        'activo',
        default=True
    )
    

    class Meta:
        verbose_name = 'Extra'
        verbose_name_plural = 'Extras'

    def __str__(self):
        return str(self.price) + " - " +  self.name

# Create your models here.
class Producto(TimeStampedModel):
    """
        Producto
    """

    

    codigo = models.CharField(
        max_length=20,
        unique=True
    )
    name = models.CharField(
        'Nombre', 
        max_length=40
    )
    
    marca = models.ForeignKey(
        Marca, 
        on_delete=models.CASCADE
    )
    
    description = models.TextField(
        'descripcion del producto',
        blank=True,
    )
    
    count = models.PositiveIntegerField(
        'cantidad en almacen',
        default=0
    )
    
    sale_price = models.DecimalField(
        'precio venta',
        max_digits=7, 
        decimal_places=2
    )
    num_sale = models.PositiveIntegerField(
        'numero de ventas',
        default=0
    )
    anulate = models.BooleanField(
        'eliminado',
        default=False
    )
    
    #
    extra = models.ManyToManyField(Extra, related_name='productos')
    image= models.ImageField( upload_to="img_productos/", null = True, blank=True)


    objects = ProductoManager()
    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    def __str__(self):
        return self.name
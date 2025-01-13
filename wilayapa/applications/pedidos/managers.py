# python
from datetime import timedelta
# django
from django.utils import timezone
from django.db import models
#
from applications.productos.models import Producto

from django.db.models import Q, Sum, F, FloatField, ExpressionWrapper,Case, When, Value



class PedidoManager(models.Manager):
    """ procedimiento para modelo venta """

    def buscar_pedido(self, kword,estado,entrega):
        # Empezamos con una consulta básica que filtra por el kword (cliente_nombre o cliente_celular)
        tpe = 3
        if entrega == 'Envio':
            tpe = 1
        elif entrega == 'Tienda':
            tpe = 0
        elif entrega == 'Delivery':
            tpe = 2
        

        if tpe <=2:
            if estado == 'Entregado':
                print("solo entragados")
                consulta = self.filter(
                    Q(cliente_nombre__icontains=kword) | Q(cliente_celular__icontains=kword) | Q(id__icontains=kword),
                    entregado=True,
                    type_entrega = tpe


                    
                )
            elif estado == 'Pendiente':
                print("solo pendientes")
                consulta = self.filter(
                    Q(cliente_nombre__icontains=kword) | Q(cliente_celular__icontains=kword) | Q(id__icontains=kword),
                    entregado=False,
                    type_entrega = tpe
                    
                )
            else:
                consulta = self.filter(
                    Q(cliente_nombre__icontains=kword) | Q(cliente_celular__icontains=kword) | Q(id__icontains=kword),
                    type_entrega = tpe
                    
                )
        else:
            if estado == 'Entregado':
                print("solo entragados")
                consulta = self.filter(
                    Q(cliente_nombre__icontains=kword) | Q(cliente_celular__icontains=kword) | Q(id__icontains=kword),
                    entregado=True,


                    
                )
            elif estado == 'Pendiente':
                print("solo pendientes")
                consulta = self.filter(
                    Q(cliente_nombre__icontains=kword) | Q(cliente_celular__icontains=kword) | Q(id__icontains=kword),
                    entregado=False
                    
                )
            else:
                consulta = self.filter(
                    Q(cliente_nombre__icontains=kword) | Q(cliente_celular__icontains=kword) | Q(id__icontains=kword),
                    
                )
        
        
        
        return consulta.order_by('-date_sale')
    def buscar_pedido_entrega(self, kword, fecha1,fecha2,estado,entrega):
        # Empezamos con una consulta básica que filtra por el kword (cliente_nombre o cliente_celular)
        tpe = 3
        if entrega == 'Envio':
            tpe = 1
        elif entrega == 'Tienda':
            tpe = 0
        elif entrega == 'Delivery':
            tpe = 2
        if tpe <=2:
            if estado == 'Entregado':
                consulta = self.filter(
                    Q(cliente_nombre__icontains=kword) | Q(cliente_celular__icontains=kword) | Q(id__icontains=kword),
                    date_entrega__range=(fecha1,fecha2),
                    entregado=True,
                    type_entrega = tpe
                )
            elif estado == 'Pendiente':
                consulta = self.filter(
                    Q(cliente_nombre__icontains=kword) | Q(cliente_celular__icontains=kword) | Q(id__icontains=kword),
                    date_entrega__range=(fecha1,fecha2),
                    entregado=False,
                    type_entrega = tpe
                )
            else :
                consulta = self.filter(
                    Q(cliente_nombre__icontains=kword) | Q(cliente_celular__icontains=kword) | Q(id__icontains=kword),
                    date_entrega__range=(fecha1,fecha2),
                    type_entrega = tpe
                )
        else:
            if estado == 'Entregado':
                consulta = self.filter(
                    Q(cliente_nombre__icontains=kword) | Q(cliente_celular__icontains=kword) | Q(id__icontains=kword),
                    date_entrega__range=(fecha1,fecha2),
                    entregado=True
                )
            elif estado == 'Pendiente':
                consulta = self.filter(
                    Q(cliente_nombre__icontains=kword) | Q(cliente_celular__icontains=kword) | Q(id__icontains=kword),
                    date_entrega__range=(fecha1,fecha2),
                    entregado=False
                )
            else :
                consulta = self.filter(
                    Q(cliente_nombre__icontains=kword) | Q(cliente_celular__icontains=kword) | Q(id__icontains=kword),
                    date_entrega__range=(fecha1,fecha2)
                )
        
        
        return consulta.order_by('-date_sale')

    
    def ventas_no_cerradas(self):
        # creamos rango de fecha
        return self.filter(
            close=False,
            anulate=False
        )
    
    def total_ventas_dia(self, user=None):
        consulta = self.filter(
            close=False,
            anulate=False
        )
        if user:
            consulta = consulta.filter(user=user)  # Filtramos por el usuario si se pasa uno
        
        consulta = consulta.aggregate(
            total=Sum('amount')
        )
        if consulta['total']:
            return consulta['total']
        else:
            return 0
    def total_ventas_dia_all(self):
        consulta = self.filter(
            close=False,
            anulate=False
        ).aggregate(
            total=Sum('amount')
        )
        if consulta['total']:
            return consulta['total']
        else:
            return 0
    def total_ventas_anuladas_dia(self, user=None):
        consulta = self.filter(
            close=False,
            anulate=True
        )
        if user:
            consulta = consulta.filter(user=user)  # Filtramos por el usuario si se pasa uno
        
        consulta = consulta.aggregate(
            total=Sum('amount')
        )
        if consulta['total']:
            return consulta['total']
        else:
            return 0
    
    def cerrar_ventas(self, user=None):
        consulta = self.filter(
            close=False,
            anulate=False
        )
        if user:
            consulta = consulta.filter(user=user)  # Filtramos por el usuario si se pasa uno
        
        # Actualizamos el estado a cerrado y sumamos el total
        total = consulta.aggregate(
            total=Sum('amount')
        )['total']
        cerrados = consulta.update(close=True)  # Devuelve número de ventas actualizadas
        # Procesamos las anulaciones, las cuales no se habían cerrado
        anulaciones = self.filter(
            anulate=True,
            close=False
        )
        if user:
            anulaciones = anulaciones.filter(user=user)
        
        anulaciones.update(close=True)
        return cerrados, total
    
    def total_ventas(self, user=None):
        consulta = self.filter(
            anulate=False,
        )
        if user:
            consulta = consulta.filter(user=user)  # Filtramos por el usuario si se pasa uno
        
        return consulta.aggregate(
            total=Sum('amount')
        )['total']
    
    def ventas_en_fechas(self, date_start, date_end):
        return self.filter(
            anulate=False,
            date_sale__range=(date_start, date_end),
        ).order_by('-date_sale')
    
    #nuevas MANAGERS
    def total_ventas_efectivo(self, user=None):
        consulta = self.filter(
            close=False,
            anulate=False,
            type_payment='1'  # '1' corresponde a 'Efectivo'
        )
        if user:
            consulta = consulta.filter(user=user)  # Filtramos por el usuario si se pasa uno
        
        consulta = consulta.aggregate(
            total=Sum('amount')
        )
        if consulta['total']:
            return consulta['total']
        else:
            return 0

    def total_ventas_transferencia(self, user=None):
        consulta = self.filter(
            close=False,
            anulate=False,
            type_payment='0'  # '0' corresponde a 'Transferencia'
        )
        if user:
            consulta = consulta.filter(user=user)  # Filtramos por el usuario si se pasa uno
        
        consulta = consulta.aggregate(
            total=Sum('amount')
        )
        if consulta['total']:
            return consulta['total']
        else:
            return 0
    

class PedidoDetailManager(models.Manager):
    """ procedimiento modelo product """
    
    def detalle_por_venta(self, id_venta):
        return self.filter(
            sale__id=id_venta
        )

    def ventas_mes_producto(self, id_prod):
        # creamos rango de fecha
        end_date = timezone.now()
        start_date = end_date - timedelta(days=30)
        
        consulta = self.filter(
            sale__anulate=False,
            created__range=(start_date, end_date),
            product__pk=id_prod,
        ).values('sale__date_sale__date', 'product__name').annotate(
            cantidad_vendida=Sum('count'),
        )
        return consulta
    
    def restablecer_stok_num_ventas(self, id_venta):
        print('validadndo functions')
        prods_en_anulados = []
        for venta_detail in self.filter(sale__id=id_venta):
            #actualizmso producot
            venta_detail.product.count = venta_detail.product.count + venta_detail.count
            venta_detail.product.num_sale = venta_detail.product.num_sale - venta_detail.count
            prods_en_anulados.append(venta_detail.product)
        Producto.objects.bulk_update(prods_en_anulados, ['count', 'num_sale'])
        return True
    

    def resumen_ventas(self):
        # Sumar por fecha y por usuario
        return self.filter(
            sale__anulate=False,  # Solo ventas no anuladas
                 
        ).values('sale__date_sale__date', 'sale__user').annotate(
            total_vendido=Sum(
                F('price_sale') * F('count'), 
                output_field=FloatField()
            ),
            total_ganancias=Sum(
                F('price_sale') * F('count'),
                output_field=FloatField()
            ),
            num_ventas=Sum('count'),
            total_efectivo=Sum(
                Case(
                    When(sale__type_payment='1', then=F('price_sale') * F('count')),
                    default=Value(0),
                    output_field=FloatField()
                )
            ),
            total_transferencia=Sum(
                Case(
                    When(sale__type_payment='0', then=F('price_sale') * F('count')),
                    default=Value(0),
                    output_field=FloatField()
                )
            ),
        )
    
    def resumen_ventas_mes(self):
        #
        return self.filter(
            sale__anulate=False
        ).values('sale__date_sale__date__month', 'sale__date_sale__date__year').annotate(
            cantidad_ventas=Sum('count'),
            total_ventas=Sum(F('price_sale')*F('count'), output_field=FloatField()),
            ganancia_total=Sum(
                F('price_sale')*F('count') - F('price_purchase')*F('count'),
                output_field=FloatField()
            )
        ).order_by('-sale__date_sale__date__month')
    
    def resumen_ventas_proveedor(self, **filters):
        # recibe 3 parametros en un diccionario
        # devuelve lista de ventas en rango de fechas de un proveedor
        # y, devuelve el total de ventas en rango de fechas y de proveedor

        if filters['date_start'] and filters['date_end'] and filters['provider']:
            consulta = self.filter(
                anulate=False,
                sale__date_sale__range = (
                    filters['date_start'],
                    filters['date_end'],
                ),
                product__provider__pk=filters['provider'],
            )
            
            lista_ventas = consulta.annotate(
                sub_total=ExpressionWrapper(
                    F('price_purchase')*F('count'),
                    output_field=FloatField()
                )
            ).order_by('sale__date_sale')

            total_ventas = consulta.aggregate(
                total_venta=Sum(
                    F('price_purchase')*F('count'),
                    output_field=FloatField()
                )
            )['total_venta']

            return lista_ventas, total_ventas
        else:
            return [], 0



class CarShopPManager(models.Manager):
    """ procedimiento modelo Carrito de compras """
    
    def total_cobrar(self, user):
        # Filtramos los productos en el carrito del usuario
        consulta = self.filter(cart__user=user)

        # Sumamos el campo 'precio_total' que ya incluye los precios del producto y los extras
        consulta = consulta.aggregate(
            total=Sum('precio_total', output_field=FloatField())
        )
        
        # Si el total es None (cuando no hay productos en el carrito), retornamos 0
        return consulta['total'] if consulta['total'] is not None else 0
class CartManager(models.Manager):
    def total_carritos(self):
        print("esto es cart manager")
    
            
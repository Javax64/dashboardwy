from django.contrib import admin
#
from .models import Sale, SaleDetail, CarShop,Cart
# Register your models here.
class SaleAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'date_sale',
        'count',
        'amount',
        'user',
        'close',
        'anulate',
    )
    list_filter = ('type_invoce', 'type_payment', 'anulate', 'user', )


class SaleDetailAdmin(admin.ModelAdmin):
    list_display = (
        'product',
        'sale',
        'count',
        'anulate',
        'tax',
    )
    search_fields = ('product__name',)


admin.site.register(Sale, SaleAdmin)
#
admin.site.register(SaleDetail, SaleDetailAdmin)
admin.site.register(Cart)
admin.site.register(CarShop)
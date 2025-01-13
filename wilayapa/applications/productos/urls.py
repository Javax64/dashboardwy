from django.urls import path
from . import views

app_name = "producto_app"
urlpatterns = [
    path(
        'add-producto/', 
        views.RegistrarProducto3.as_view(),
        name='producto-add',
    ),
    path(
        'lista-producto/', 
        views.ProductoListView.as_view(),
        name='producto-lista',
    ),
    path(
        'producto/eliminar/<pk>/', 
        views.ProductDeleteView.as_view(),
        name='producto-delete',
    ),
    path(
        'producto/<int:producto_id>/actualizar/', 
        views.UpdateProductView.as_view(),
        name='producto-update',
    ),
    path(
        'producto/scannerProductos/', 
        views.SacannerStockFormView.as_view(),
        name='producto-scanner',
    ),
    path('delete_qr_image/', views.DeleteQRImageView.as_view(), name='delete_qr_image'),
    path(
        'producto/pruebaScanner/', 
        views.PruebaFormView.as_view(),
        name='prueba-scanner',
    ),
    path(
        'producto/inventarioProductos/', 
        views.ScannerInventario.as_view(),
        name='producto-inventario',
    ),
    
    
]

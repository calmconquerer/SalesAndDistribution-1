from django.urls import path
from . import views

urlpatterns = [
    path('add_item/', views.add_item, name='add-item'),
    path('stock/', views.stock, name='stock'),
    path('edit_item/<pk>', views.edit_item, name='edit-item'),
    path('delete_item/<pk>', views.delete_item, name='delete-item'),
]

from django.urls import path
from app import views

app_name = 'vault'

urlpatterns = [
    # Kirish va Chiqish (Lock Screen)
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Asosiy Ombor (Vault) - Barcha parollar ro'yxati
    path('', views.vault_view, name='vault'),

    # CRUD amallari
    path('add/', views.add_credential, name='add_entry'),
    path('edit/<int:pk>/', views.edit_credential, name='edit_entry'),
    path('delete/<int:pk>/', views.delete_credential, name='delete_entry'),
    path('export/', views.export_credentials, name='export_credentials'),
    path('settings/', views.settings_view, name='settings'),
]
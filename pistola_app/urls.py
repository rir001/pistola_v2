# nombre_de_tu_app/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.loan_dashboard, name='loan_dashboard'),
    path('create-loan/', views.create_loan, name='create_loan'),
    path('return-loan/<int:loan_id>/', views.return_loan, name='return_loan'),
    path('search-objects/', views.search_objects, name='search_objects'),
    path('search-persons/', views.search_persons, name='search_persons'),
    
    # Gestión de objetos
    path('objects/', views.objects_management, name='objects_management'),
    path('objects/create-bulk/', views.create_objects_bulk, name='create_objects_bulk'),
    path('objects/create-kind/', views.create_kind, name='create_kind'),
]
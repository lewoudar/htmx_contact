from django.urls import path

from . import views

app_name = 'contact'
urlpatterns = [
    path('', views.index, name='index'),
    path('new/', views.ContactCreate.as_view(), name='create'),
    path('<int:contact_id>/', views.ReadEditDeleteContact.as_view(), name='show-delete'),
    path('<int:contact_id>/edit/', views.ContactEdit.as_view(), name='edit'),
    path('email/', views.check_email, name='check-email')
]

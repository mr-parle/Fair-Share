from django.urls import path
from . import views

urlpatterns = [
    path('create_group/', views.create_group, name='create_group'),
    
    path('create_group/', views.create_group, name='create_group'),
    path('group/<uuid:group_id>/', views.group_detail, name='group_detail'),
    # path('add_member/<uuid:group_id>/', views.add_member, name='add_member'),
    path('groups/<uuid:group_id>/add_transaction/', views.add_transaction, name='add_transaction'),
    path('groups/<uuid:group_id>/transactions/', views.transaction_list, name='transaction_list'),
    path('split_expenses/<uuid:group_id>', views.split_expenses, name='split_expenses'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('go_back/', views.go_back, name='go_back'),
    # path('group_detail/<int:pk>/', views.group_detail, name='group_detail'),
]

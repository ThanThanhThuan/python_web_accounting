# accounts/urls.py
from django.urls import path
from . import views

# accounts/urls.py
urlpatterns = [
    path('', views.AccountListView.as_view(), name='account_list'),
    path('create/', views.AccountCreateView.as_view(), name='account_create'),
    path('update/<int:pk>/', views.AccountUpdateView.as_view(), name='account_update'),
    path('delete/<int:pk>/', views.AccountDeleteView.as_view(), name='account_delete'),
    
    # NEW URLs
    path('journal/', views.JournalEntryListView.as_view(), name='journal_list'),
    path('journal/create/', views.JournalEntryCreateView.as_view(), name='journal_create'),
    path('report/trial-balance/', views.trial_balance, name='trial_balance'),
    path('report/ledger/', views.general_ledger, name='general_ledger'),
]
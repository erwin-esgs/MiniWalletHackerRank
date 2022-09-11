from django.urls import path

from . import views

urlpatterns = [
    path('init', views.InitView.as_view(), name='init'),
    path('wallet', views.WalletView.as_view(), name='wallet'),
    path('wallet/deposits', views.DepositsView.as_view(), name='deposits'),
    path('wallet/withdrawals', views.WithdrawalsView.as_view(), name='withdrawals'),
]
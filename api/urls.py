from django.urls import path
from . import views

urlpatterns = [
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/profile/', views.profile_view, name='profile'),
    
    path('dashboard/stats/', views.dashboard_stats, name='dashboard_stats'),
    
    path('jenis-layanan/', views.JenisLayananListCreateView.as_view(), name='jenis_layanan_list_create'),
    path('jenis-layanan/<int:pk>/', views.JenisLayananDetailView.as_view(), name='jenis_layanan_detail'),
    
    path('penerima/', views.PenerimaListCreateView.as_view(), name='penerima_list_create'),
    path('penerima/<int:pk>/', views.PenerimaDetailView.as_view(), name='penerima_detail'),
    
    path('pengiriman/', views.PengirimanListView.as_view(), name='pengiriman_list'),
    path('pengiriman/create/', views.PengirimanCreateView.as_view(), name='pengiriman_create'),
    path('pengiriman/<int:pk>/', views.PengirimanDetailView.as_view(), name='pengiriman_detail'),
    
    path('paket/', views.PaketListCreateView.as_view(), name='paket_list_create'),
    path('paket/<int:pk>/', views.PaketDetailView.as_view(), name='paket_detail'),
    
    path('riwayat-pengiriman/', views.RiwayatPengirimanListCreateView.as_view(), name='riwayat_pengiriman_list_create'), # tracking_log_list_create diubah
    path('riwayat-pengiriman/<int:pk>/', views.RiwayatPengirimanDetailView.as_view(), name='riwayat_pengiriman_detail'), # tracking_log_detail diubah
    
    path('tracking/<str:nomor_resi>/', views.tracking_by_resi, name='tracking_by_resi'),
    

    path('users/', views.UserListView.as_view(), name='user_list'),
    path('users/<int:pk>/', views.UserDetailView.as_view(), name='user_detail'),
]
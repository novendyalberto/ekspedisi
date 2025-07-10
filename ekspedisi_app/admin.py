from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, JenisLayanan, Penerima, Pengiriman, Paket, RiwayatPengiriman

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_active', 'created_at')
    list_filter = ('role', 'is_active', 'created_at')
    search_fields = ('username', 'email')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Info Tambahan', {'fields': ('role',)}),
    )

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('nama_lengkap', 'user', 'nomor_telepon', 'is_active')
    search_fields = ('nama_lengkap', 'nomor_telepon')
    list_filter = ('is_active',)

@admin.register(JenisLayanan)
class JenisLayananAdmin(admin.ModelAdmin):
    list_display = ('nama_layanan', 'tarif_per_kg', 'is_active')
    search_fields = ('nama_layanan',)
    list_filter = ('is_active',)

@admin.register(Penerima)
class PenerimaAdmin(admin.ModelAdmin):
    list_display = ('nama_penerima', 'kota_tujuan', 'nomor_telepon_penerima', 'is_active')
    search_fields = ('nama_penerima', 'kota_tujuan')
    list_filter = ('kota_tujuan', 'is_active')

@admin.register(Pengiriman)
class PengirimanAdmin(admin.ModelAdmin):
    list_display = ('nomor_resi', 'pengirim', 'status_pengiriman', 'total_berat', 'total_biaya', 'tanggal_pengiriman')
    search_fields = ('nomor_resi', 'pengirim__username')
    list_filter = ('status_pengiriman', 'jenis_layanan', 'tanggal_pengiriman')
    readonly_fields = ('nomor_resi', 'total_berat', 'total_biaya')

@admin.register(Paket)
class PaketAdmin(admin.ModelAdmin):
    list_display = ('kode_paket', 'nama_barang', 'jenis_paket', 'berat', 'pengiriman')
    search_fields = ('kode_paket', 'nama_barang')
    list_filter = ('jenis_paket', 'asuransi', 'pengiriman__status_pengiriman')
    readonly_fields = ('kode_paket',)

@admin.register(RiwayatPengiriman)
class RiwayatPengirimanAdmin(admin.ModelAdmin):
    list_display = ('pengiriman', 'status', 'lokasi', 'waktu')
    search_fields = ('pengiriman__nomor_resi', 'status', 'lokasi')
    list_filter = ('status', 'waktu')

admin.site.register(User, CustomUserAdmin)
admin.site.site_header = "Admin Sistem Ekspedisi"
admin.site.site_title = "Ekspedisi Admin"
admin.site.index_title = "Dashboard Admin Ekspedisi"
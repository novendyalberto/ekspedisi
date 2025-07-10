from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from PIL import Image
import os

def compress_image(image_path, quality=85):
    """Fungsi untuk mengkompresi gambar"""
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img.save(image_path, optimize=True, quality=quality)

def increment_resi_number():
    """Fungsi untuk membuat nomor resi otomatis"""
    last_shipment = Pengiriman.objects.filter(
        nomor_resi__startswith='EKS'
    ).order_by('-id').first()
    
    if last_shipment:
        last_number = int(last_shipment.nomor_resi[3:])
        new_number = last_number + 1
    else:
        new_number = 1
    
    return f"EKS{new_number:06d}"

def increment_paket_code():
    """Fungsi untuk membuat kode paket otomatis"""
    last_paket = Paket.objects.filter(
        kode_paket__startswith='PKT'
    ).order_by('-id').first()
    
    if last_paket:
        last_number = int(last_paket.kode_paket[3:])
        new_number = last_number + 1
    else:
        new_number = 1
    
    return f"PKT{new_number:06d}"

class User(AbstractUser):
    """Model User dengan role yang diperluas"""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('staf', 'Staf'),
        ('kurir', 'Kurir'),
        ('pelanggan', 'Pelanggan'),
    ]
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='pelanggan')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.username} ({self.role})"

class StatusModel(models.Model):
    """Abstract model untuk status"""
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True

class Profile(StatusModel):
    """Model Profile untuk informasi detail user"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    nama_lengkap = models.CharField(max_length=255)
    alamat = models.TextField()
    nomor_telepon = models.CharField(max_length=20)
    email = models.EmailField()
    foto_profil = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.foto_profil:
            compress_image(self.foto_profil.path)
    
    def __str__(self):
        return f"Profile: {self.nama_lengkap}"

class JenisLayanan(StatusModel):
    """Model untuk jenis layanan ekspedisi"""
    nama_layanan = models.CharField(max_length=100)
    deskripsi = models.TextField()
    tarif_per_kg = models.DecimalField(max_digits=10, decimal_places=2)
    
    class Meta:
        verbose_name = "Jenis Layanan"
        verbose_name_plural = "Jenis Layanan"
    
    def __str__(self):
        return self.nama_layanan

class Penerima(StatusModel):
    """Model untuk data penerima paket"""
    nama_penerima = models.CharField(max_length=255)
    alamat_penerima = models.TextField()
    nomor_telepon_penerima = models.CharField(max_length=20)
    kota_tujuan = models.CharField(max_length=100)
    kode_pos = models.CharField(max_length=10)
    
    class Meta:
        verbose_name = "Penerima"
        verbose_name_plural = "Penerima"
    
    def __str__(self):
        return f"{self.nama_penerima} - {self.kota_tujuan}"

class Pengiriman(StatusModel):
    """Model untuk data pengiriman"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('pickup', 'Pickup'),
        ('transit', 'Transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    pengirim = models.ForeignKey(User, on_delete=models.CASCADE, related_name='pengiriman_pengirim')
    kurir = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                             related_name='pengiriman_kurir', limit_choices_to={'role': 'kurir'})
    nomor_resi = models.CharField(max_length=20, unique=True, default=increment_resi_number)
    tanggal_pengiriman = models.DateTimeField(default=timezone.now)
    status_pengiriman = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    jenis_layanan = models.ForeignKey(JenisLayanan, on_delete=models.CASCADE)
    total_berat = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_biaya = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    catatan = models.TextField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Pengiriman"
        verbose_name_plural = "Pengiriman"
        ordering = ['-tanggal_pengiriman']
    
    def __str__(self):
        return f"Resi: {self.nomor_resi} - {self.pengirim.username}"
    
    def calculate_total(self):
        """Hitung total berat dan biaya"""
        paket_list = self.paket_set.all()
        self.total_berat = sum(paket.berat for paket in paket_list)
        self.total_biaya = self.total_berat * self.jenis_layanan.tarif_per_kg
        self.save()

class Paket(StatusModel):
    """Model untuk paket dalam pengiriman"""
    JENIS_PAKET_CHOICES = [
        ('kecil', 'Paket Kecil'),
        ('kargo', 'Kargo'),
    ]
    
    pengiriman = models.ForeignKey(Pengiriman, on_delete=models.CASCADE, related_name='paket_set')
    penerima = models.ForeignKey(Penerima, on_delete=models.CASCADE)
    kode_paket = models.CharField(max_length=20, unique=True, default=increment_paket_code)
    nama_barang = models.CharField(max_length=255)
    deskripsi_barang = models.TextField()
    berat = models.DecimalField(max_digits=10, decimal_places=2)
    panjang = models.DecimalField(max_digits=10, decimal_places=2)
    lebar = models.DecimalField(max_digits=10, decimal_places=2)
    tinggi = models.DecimalField(max_digits=10, decimal_places=2)
    jenis_paket = models.CharField(max_length=20, choices=JENIS_PAKET_CHOICES, default='kecil')
    nilai_barang = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    asuransi = models.BooleanField(default=False)
    foto_paket = models.ImageField(upload_to='paket_pics/', blank=True, null=True)
    
    class Meta:
        verbose_name = "Paket"
        verbose_name_plural = "Paket"
    
    def __str__(self):
        return f"{self.kode_paket} - {self.nama_barang}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.foto_paket:
            compress_image(self.foto_paket.path)
        # Update total pengiriman
        self.pengiriman.calculate_total()

class RiwayatPengiriman(StatusModel):
    """Model untuk riwayat pengiriman"""
    pengiriman = models.ForeignKey(Pengiriman, on_delete=models.CASCADE, related_name='riwayat_pengiriman')
    status = models.CharField(max_length=100)
    keterangan = models.TextField()
    lokasi = models.CharField(max_length=255)
    waktu = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "Riwayat Pengiriman"
        verbose_name_plural = "Riwayat Pengiriman" 
        ordering = ['-waktu']
    
    def __str__(self):
        return f"{self.pengiriman.nomor_resi} - {self.status}"
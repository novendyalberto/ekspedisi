from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from ekspedisi_app.models import (
    User, Profile, JenisLayanan, Penerima, 
    Pengiriman, Paket, RiwayatPengiriman
)

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password_confirm', 'role')
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError("Password tidak cocok")
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError('Username atau password salah')
            if not user.is_active:
                raise serializers.ValidationError('Akun tidak aktif')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Username dan password harus diisi')
        
        return attrs

class ProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    role = serializers.CharField(source='user.role', read_only=True)
    
    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ('user', 'created_at', 'updated_at')

class JenisLayananSerializer(serializers.ModelSerializer):
    class Meta:
        model = JenisLayanan
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class PenerimaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Penerima
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class RiwayatPengirimanSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiwayatPengiriman 
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class PaketSerializer(serializers.ModelSerializer):
    penerima_detail = PenerimaSerializer(source='penerima', read_only=True)
    
    class Meta:
        model = Paket
        fields = '__all__'
        read_only_fields = ('kode_paket', 'created_at', 'updated_at')

class PengirimanSerializer(serializers.ModelSerializer):
    pengirim_username = serializers.CharField(source='pengirim.username', read_only=True)
    kurir_username = serializers.CharField(source='kurir.username', read_only=True)
    jenis_layanan_detail = JenisLayananSerializer(source='jenis_layanan', read_only=True)
    paket_list = PaketSerializer(source='paket_set', many=True, read_only=True)
    riwayat_pengiriman = RiwayatPengirimanSerializer(many=True, read_only=True) 
    
    class Meta:
        model = Pengiriman
        fields = '__all__'
        read_only_fields = ('nomor_resi', 'pengirim', 'total_berat', 'total_biaya', 'created_at', 'updated_at')

class PengirimanCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pengiriman
        fields = ('jenis_layanan', 'catatan')
    
    def create(self, validated_data):
        validated_data['pengirim'] = self.context['request'].user
        return super().create(validated_data)

class UserSerializer(serializers.ModelSerializer):
    profile = ProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'role', 'is_active', 'created_at', 'profile')
        read_only_fields = ('created_at',)
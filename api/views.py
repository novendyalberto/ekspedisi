from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from django.contrib.auth import login, logout
from django.shortcuts import get_object_or_404

from ekspedisi_app.models import (
    User, Profile, JenisLayanan, Penerima, 
    Pengiriman, Paket, RiwayatPengiriman
)
from .serializers import (
    UserRegistrationSerializer, LoginSerializer, ProfileSerializer,
    JenisLayananSerializer, PenerimaSerializer, PengirimanSerializer,
    PaketSerializer, RiwayatPengirimanSerializer, UserSerializer,
    PengirimanCreateSerializer
)

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """API untuk registrasi user baru"""
    serializer = UserRegistrationSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Registrasi berhasil',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            },
            'token': token.key
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """API untuk login user"""
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        login(request, user)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'message': 'Login berhasil',
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            },
            'token': token.key
        }, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """API untuk logout user"""
    try:
        request.user.auth_token.delete()
        logout(request)
        return Response({
            'message': 'Logout berhasil'
        }, status=status.HTTP_200_OK)
    except:
        return Response({
            'message': 'Logout gagal'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """API untuk melihat profile user"""
    try:
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Profile.DoesNotExist:
        return Response({
            'message': 'Profile tidak ditemukan'
        }, status=status.HTTP_404_NOT_FOUND)

# CRUD Views untuk Jenis Layanan
class JenisLayananListCreateView(generics.ListCreateAPIView):
    queryset = JenisLayanan.objects.filter(is_active=True)
    serializer_class = JenisLayananSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['nama_layanan']

class JenisLayananDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = JenisLayanan.objects.filter(is_active=True)
    serializer_class = JenisLayananSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

# CRUD Views untuk Penerima
class PenerimaListCreateView(generics.ListCreateAPIView):
    queryset = Penerima.objects.filter(is_active=True)
    serializer_class = PenerimaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['nama_penerima', 'kota_tujuan']

class PenerimaDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Penerima.objects.filter(is_active=True)
    serializer_class = PenerimaSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

# CRUD Views untuk Pengiriman
class PengirimanListView(generics.ListAPIView):
    serializer_class = PengirimanSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['status_pengiriman', 'jenis_layanan__nama_layanan']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Pengiriman.objects.filter(is_active=True)
        elif user.role == 'kurir':
            return Pengiriman.objects.filter(kurir=user, is_active=True)
        else:
            return Pengiriman.objects.filter(pengirim=user, is_active=True)

class PengirimanCreateView(generics.CreateAPIView):
    serializer_class = PengirimanCreateSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

class PengirimanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PengirimanSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Pengiriman.objects.filter(is_active=True)
        elif user.role == 'kurir':
            return Pengiriman.objects.filter(kurir=user, is_active=True)
        else:
            return Pengiriman.objects.filter(pengirim=user, is_active=True)

# CRUD Views untuk Paket
class PaketListCreateView(generics.ListCreateAPIView):
    serializer_class = PaketSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['jenis_paket', 'pengiriman__status_pengiriman']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Paket.objects.filter(is_active=True)
        elif user.role == 'kurir':
            return Paket.objects.filter(pengiriman__kurir=user, is_active=True)
        else:
            return Paket.objects.filter(pengiriman__pengirim=user, is_active=True)

class PaketDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PaketSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Paket.objects.filter(is_active=True)
        elif user.role == 'kurir':
            return Paket.objects.filter(pengiriman__kurir=user, is_active=True)
        else:
            return Paket.objects.filter(pengiriman__pengirim=user, is_active=True)


class RiwayatPengirimanListCreateView(generics.ListCreateAPIView): 
    serializer_class = RiwayatPengirimanSerializer 
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['pengiriman__nomor_resi', 'status']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return RiwayatPengiriman.objects.filter(is_active=True) 
        elif user.role == 'kurir':
            return RiwayatPengiriman.objects.filter(pengiriman__kurir=user, is_active=True) 
        else:
            return RiwayatPengiriman.objects.filter(pengiriman__pengirim=user, is_active=True) 

class RiwayatPengirimanDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = RiwayatPengirimanSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return RiwayatPengiriman.objects.filter(is_active=True)
        elif user.role == 'kurir':
            return RiwayatPengiriman.objects.filter(pengiriman__kurir=user, is_active=True)
        else:
            return RiwayatPengiriman.objects.filter(pengiriman__pengirim=user, is_active=True) 

@api_view(['GET'])
@permission_classes([AllowAny])
def tracking_by_resi(request, nomor_resi):
    """API untuk tracking pengiriman berdasarkan nomor resi"""
    try:
        pengiriman = Pengiriman.objects.get(nomor_resi=nomor_resi, is_active=True)
        serializer = PengirimanSerializer(pengiriman)
        return Response({
            'message': 'Data tracking ditemukan',
            'data': serializer.data
        }, status=status.HTTP_200_OK)
    except Pengiriman.DoesNotExist:
        return Response({
            'message': 'Nomor resi tidak ditemukan'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """API untuk mendapatkan statistik dashboard"""
    user = request.user
    
    if user.role == 'admin':
        total_pengiriman = Pengiriman.objects.filter(is_active=True).count()
        pengiriman_pending = Pengiriman.objects.filter(status_pengiriman='pending', is_active=True).count()
        pengiriman_transit = Pengiriman.objects.filter(status_pengiriman='transit', is_active=True).count()
        pengiriman_delivered = Pengiriman.objects.filter(status_pengiriman='delivered', is_active=True).count()
        total_paket = Paket.objects.filter(is_active=True).count()
        total_user = User.objects.filter(is_active=True).count()
    else:
        total_pengiriman = Pengiriman.objects.filter(pengirim=user, is_active=True).count()
        pengiriman_pending = Pengiriman.objects.filter(pengirim=user, status_pengiriman='pending', is_active=True).count()
        pengiriman_transit = Pengiriman.objects.filter(pengirim=user, status_pengiriman='transit', is_active=True).count()
        pengiriman_delivered = Pengiriman.objects.filter(pengirim=user, status_pengiriman='delivered', is_active=True).count()
        total_paket = Paket.objects.filter(pengiriman__pengirim=user, is_active=True).count()
        total_user = 1
    
    return Response({
        'total_pengiriman': total_pengiriman,
        'pengiriman_pending': pengiriman_pending,
        'pengiriman_transit': pengiriman_transit,
        'pengiriman_delivered': pengiriman_delivered,
        'total_paket': total_paket,
        'total_user': total_user
    }, status=status.HTTP_200_OK)


class UserListView(generics.ListAPIView):
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['role', 'is_active']
    
    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return User.objects.all()
        else:
            return User.objects.none()

class UserDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user
        obj = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        if user.role != 'admin' and user != obj:
            self.permission_denied(self.request)
        return obj
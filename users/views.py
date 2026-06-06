from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User
from .serializers import UserSerializer,RegisterSerializer,ChangePasswordSerializer

# Create your views here.
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]
    
class LoginView(APIView):
    permission_classes=[AllowAny]
    
    def post(self, request):
        from django.contrib.auth import authenticate
        username = request.data.get('username')
        password = request.data.get('password')
        
        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {'detail': 'Invalid credentials'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        if not user.is_active:
            return Response(
                {'detail': 'Account is disabled'},
                status=status.HTTP_403_FORBIDDEN
            )
            
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refesh': str(refresh),
            'user': UserSerializer(user).data,
        })
        
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({'detail':'Logout successfully'})
        except Exception:
            return Response(
                {'detail':'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
class ProfileView(generics.RetrieveUpdateAPIView):
    serializers_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    
    def get_object(self):
        return self.request.user
    
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self,request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context = {'request': request}
        )
        if serializer.is_valid:
            serializer.save()
            return Response({'detail': 'Password changed successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserListView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if not self.request.user.is_admin:
            return User.objects.filter(id=self.request.user.id)
        return User.objects.all()
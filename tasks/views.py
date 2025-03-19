from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.models import User

@api_view(['GET'])
@permission_classes([IsAuthenticated])  # Protect this API with JWT
def protected_view(request):
    return Response({'message': 'You have access to this API!'})

from tasks.serializers import UserSerializer
from rest_framework.permissions import AllowAny

@api_view(['POST'])
@permission_classes([AllowAny])  # Allow anyone to register
def register(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'username': user.username,
            'email': user.email,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

from rest_framework import viewsets
from .models import Task
from .serializers import TaskSerializer
from .permissions import IsTaskOwnerOrAdmin
from django_filters.rest_framework import DjangoFilterBackend

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'status': ['exact'],  # Filter by 'pending' or 'completed'
        'priority': ['exact'],  # Filter by 'low', 'medium', 'high'
        'created_at': ['gte', 'lte'],  # Greater than or equal to, less than or equal to
        'updated_at': ['gte', 'lte'],
    }

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.is_staff:
            return Task.objects.all().order_by('-created_at')  # Order by creation date, descending
        return Task.objects.filter(created_by=user).order_by('-created_at')  # Order by creation date, descending

    def get_permissions(self):
        if self.action in ['update', 'partial_update', 'destroy']:
            self.permission_classes = [IsAuthenticated, IsTaskOwnerOrAdmin]
        return super().get_permissions()
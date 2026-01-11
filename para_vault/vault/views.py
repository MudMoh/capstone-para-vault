from rest_framework import viewsets, permissions, filters, generics, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Container, Note
from .serializers import ContainerSerializer, NoteSerializer, UserSerializer

class IsOwner(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to access/edit it.
    """
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user

class ContainerViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD for P.A.R.A. Containers.
    """
    serializer_class = ContainerSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    
    def get_queryset(self):
        # Users only see containers they own 
        queryset = Container.objects.filter(owner=self.request.user)
        # Support filtering by type (P, A, R, or ARCHIVE) 
        container_type = self.request.query_params.get('type')
        if container_type:
            queryset = queryset.filter(type=container_type)
        return queryset

    def perform_create(self, serializer):
        # Automatically set the owner to the current user
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=['get'])
    def notes(self, request, pk=None):
        """
        GET /api/containers/<id>/notes/
        Retrieve all notes linked to this specific container.
        """
        container = self.get_object()
        notes = container.notes.all()
        serializer = NoteSerializer(notes, many=True)
        return Response(serializer.data)

class NoteViewSet(viewsets.ModelViewSet):
    """
    Handles CRUD for Notes, including soft-delete and search.
    """
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'content'] # Supports global search 

    def get_queryset(self):
        # Users only see notes they own 
        return Note.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        # Automatically set the owner to the current user
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        # Soft delete logic: archive instead of deleting 
        instance.is_archived = True
        instance.save()

    @action(detail=True, methods=['post'])
    def link(self, request, pk=None):
        """
        POST /api/notes/<id>/link/
        Expects: {"container_ids": [1, 2]}
        """
        note = self.get_object()
        container_ids = request.data.get('container_ids', [])
        # Only allow linking to containers owned by the user
        containers = Container.objects.filter(id__in=container_ids, owner=request.user)
        note.containers.add(*containers)
        return Response({'status': 'linked successfully'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])
    def unlink(self, request, pk=None):
        """
        POST /api/notes/<id>/unlink/
        Expects: {"container_ids": [1]}
        """
        note = self.get_object()
        container_ids = request.data.get('container_ids', [])
        containers = Container.objects.filter(id__in=container_ids, owner=request.user)
        note.containers.remove(*containers)
        return Response({'status': 'unlinked successfully'}, status=status.HTTP_200_OK)

class RegisterView(generics.CreateAPIView):
    """
    POST /api/users/register/
    Create a new user account. 
    """
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny] # Public 
    serializer_class = UserSerializer

    def perform_create(self, serializer):
        # Hash the password before saving
        user = serializer.save()
        user.set_password(self.request.data.get('password'))
        user.save()

class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    GET/PATCH /api/users/profile/
    Manage the authenticated user's profile. 
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user
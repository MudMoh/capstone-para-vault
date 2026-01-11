from rest_framework import viewsets, permissions, filters
from .models import Container, Note
from .serializers import ContainerSerializer, NoteSerializer

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
        queryset = Container.objects.filter(owner=self.user)
        # Support filtering by type (P, A, R, or A) 
        container_type = self.request.query_params.get('type')
        if container_type:
            queryset = queryset.filter(type=container_type)
        return queryset

    def perform_create(self, serializer):
        # Automatically set the owner to the current user [cite: 11]
        serializer.save(owner=self.request.user)

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
        # Automatically set the owner to the current user [cite: 14]
        serializer.save(owner=self.request.user)

    def perform_destroy(self, instance):
        # Soft delete logic: archive instead of deleting 
        instance.is_archived = True
        instance.save()
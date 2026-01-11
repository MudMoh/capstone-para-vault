from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from .views import ContainerViewSet, NoteViewSet

router = DefaultRouter()
router.register(r'containers', ContainerViewSet, basename='container')
router.register(r'notes', NoteViewSet, basename='note')

urlpatterns = [
    # User Endpoints 
    path('users/register/', RegisterView.as_view(), name='register'),
    path('users/login/', TokenObtainPairView.as_view(), name='login'), # JWT Token 
    path('users/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('users/profile/', UserProfileView.as_view(), name='profile'),
    path('', include(router.urls)),
]
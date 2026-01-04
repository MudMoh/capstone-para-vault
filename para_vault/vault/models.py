from django.db import models

# Create your models here.
from django.contrib.auth.models import User

class Container(models.Model):
    """
    Represents the P.A.R.A. structure: Proj cts, Areas, Resources, and Archives[cite: 10].
    """
    # Choice field: Must be one of 'P', 'A', 'R', or 'A'.
    PARA_CHOICES = [
        ('P', 'Project'),
        ('A', 'Area'),
        ('R', 'Resource'),
        ('ARCHIVE', 'Archive'), # Using 'ARCHIVE' to distinguish from 'Area' internally if needed
    ]

    name = models.CharField(max_length=100) # 
    type = models.CharField(max_length=10, choices=PARA_CHOICES) # 
    description = models.TextField(blank=True, null=True) # Optional 
    created_at = models.DateTimeField(auto_now_add=True) # Auto-generated 
    updated_at = models.DateTimeField(auto_now=True) # Auto-updated 
    
    # RELATIONSHIP (One-to-Many): Links the container to its owner[cite: 11, 16].
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='containers')

    def __str__(self):
        return f"{self.name} ({self.get_type_display()})"

class Note(models.Model):
    """
    The atomic knowledge unit holding core content[cite: 12, 13].
    """
    title = models.CharField(max_length=255) # [cite: 14]
    content = models.TextField() # Required [cite: 14]
    is_archived = models.BooleanField(default=False) # Used for soft-deletion [cite: 14, 25]
    created_at = models.DateTimeField(auto_now_add=True) # [cite: 14]
    updated_at = models.DateTimeField(auto_now=True) # [cite: 14]

    # RELATIONSHIP (One-to-Many): Links the note to its owner[cite: 14, 16].
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    
    # RELATIONSHIP (Many-to-Many): Links the note to one or more P.A.R.A. containers[cite: 14, 16].
    containers = models.ManyToManyField(Container, related_name='notes', blank=True)

    def __str__(self):
        return self.title
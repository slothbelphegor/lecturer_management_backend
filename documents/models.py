from django.db import models

# Create your models here.
class Document(models.Model):
    name = models.CharField(max_length=100)
    file_link = models.URLField(max_length=200)
    published_at = models.DateTimeField(null=True, blank=True)
    valid_at = models.DateTimeField(null=True, blank=True)
    published_by = models.CharField(max_length=100, null=True, blank=True)
    signed_by = models.CharField(max_length=100, null=True, blank=True)
    type = models.CharField(max_length=100)
    
    class Meta:
        permissions = (
            ("can_view_document", "Can view document"),
            ("can_add_document", "Can add document"),
            ("can_change_document", "Can change document"),
            ("can_delete_document", "Can delete document"),
        )
    
    def __str__(self):
        return self.name
from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Subject)
admin.site.register(Lecturer)
admin.site.register(Evaluation)
admin.site.register(Schedule)
admin.site.register(LecturerRecommendation)

from django.contrib import admin  # noqa
from .models import (
    UserProfile,
    Survey,
)

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Survey)

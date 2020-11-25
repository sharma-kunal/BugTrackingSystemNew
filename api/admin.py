from django.contrib import admin
from .models import Projects, Company, Tickets

# Register your models here.

admin.site.register(Projects)
admin.site.register(Company)
admin.site.register(Tickets)

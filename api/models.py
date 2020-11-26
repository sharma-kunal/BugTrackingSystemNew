from django.db import models
from django.contrib.auth.models import User

# Create your models here.


# If user is in this table:
#       means that user is Company
# else
#       means that user is Client
class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, unique=True)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)


class Projects(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField(max_length=1000)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    company_id = models.ForeignKey(Company, on_delete=models.CASCADE)


class Tickets(models.Model):
    PRIORITY_CHOICES = (
        ('Low', 'Low'),
        ('Medium', 'Medium'),
        ('High', 'High')
    )
    STATUS_CHOICES = (
        ('Open', 'Open'),
        ('Closed', 'Closed')
    )
    TICKET_TYPE_CHOICES = (
        ('Feature/Request', 'Feature/Request'),
        ('Bug/Error', 'Bug/Error'),
        ('Others', 'Others')
    )

    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    type = models.CharField(max_length=20, choices=TICKET_TYPE_CHOICES)
    CreatedDate = models.DateTimeField(auto_now_add=True)
    project_id = models.ForeignKey(Projects, on_delete=models.CASCADE)

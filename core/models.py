from django.db import models
from django.contrib.auth.models import User


class Customer(models.Model):
    LEAD = 'lead'
    OPPORTUNITY = 'opportunity'
    CUSTOMER = 'customer'
    ARCHIVED = 'archived'

    STATUS_CHOICES = [
        (LEAD, 'Lead'),
        (OPPORTUNITY, 'Opportunity'),
        (CUSTOMER, 'Customer'),
        (ARCHIVED, 'Archived'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    company = models.CharField(max_length=100, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=LEAD)
    notes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='customers')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Interaction(models.Model):
    CALL = 'call'
    MEETING = 'meeting'
    EMAIL = 'email'
    OTHER = 'other'

    INTERACTION_TYPE_CHOICES = [
        (CALL, 'Call'),
        (MEETING, 'Meeting'),
        (EMAIL, 'Email'),
        (OTHER, 'Other'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='interactions')
    interaction_type = models.CharField(max_length=10, choices=INTERACTION_TYPE_CHOICES)
    date = models.DateTimeField()
    notes = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_interactions')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_interaction_type_display()} with {self.customer} on {self.date.strftime('%Y-%m-%d')}"

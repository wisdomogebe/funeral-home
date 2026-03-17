"""
Django app configuration for FHMS.
"""
from django.apps import AppConfig


class FhmsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'fhms'
    verbose_name = 'Funeral Home Management System'

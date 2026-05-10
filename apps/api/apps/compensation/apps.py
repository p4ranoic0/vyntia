"""Django AppConfig for the compensation bounded context (B.7).

Hosts Ley 30709 CCF + Category + SalaryBand + factor scoring models, plus
salary-gap audit and Excel import services.
"""
from django.apps import AppConfig


class CompensationConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.compensation"
    label = "compensation"
    verbose_name = "Compensación (Ley 30709)"

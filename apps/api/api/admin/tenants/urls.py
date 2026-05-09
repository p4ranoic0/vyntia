from django.urls import path

from api.admin.tenants.views import TenantDetailView, TenantsListCreateView

app_name = "admin_tenants"

urlpatterns = [
    path("", TenantsListCreateView.as_view(), name="list_create"),
    path("<uuid:tenant_id>/", TenantDetailView.as_view(), name="detail"),
    # lifecycle actions added in Task 4
]

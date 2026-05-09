from django.urls import path

from api.admin.tenants.views import (
    TenantCancelView,
    TenantDetailView,
    TenantReinviteView,
    TenantsListCreateView,
    TenantSuspendView,
)

app_name = "admin_tenants"

urlpatterns = [
    path("", TenantsListCreateView.as_view(), name="list_create"),
    path("<uuid:tenant_id>/", TenantDetailView.as_view(), name="detail"),
    path("<uuid:tenant_id>/suspend/", TenantSuspendView.as_view(), name="suspend"),
    path("<uuid:tenant_id>/cancel/", TenantCancelView.as_view(), name="cancel"),
    path("<uuid:tenant_id>/invitations/", TenantReinviteView.as_view(), name="reinvite"),
]

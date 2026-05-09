from django.urls import path

from api.v1.workspaces.views import WorkspacesListView

app_name = "workspaces"

urlpatterns = [
    path("", WorkspacesListView.as_view(), name="list"),
    # /<slug>/exchange/ added in Task 5
]

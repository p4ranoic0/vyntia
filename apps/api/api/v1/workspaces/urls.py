from django.urls import path

from api.v1.workspaces.views import WorkspaceExchangeView, WorkspacesListView

app_name = "workspaces"

urlpatterns = [
    path("", WorkspacesListView.as_view(), name="list"),
    path("<slug:slug>/exchange/", WorkspaceExchangeView.as_view(), name="exchange"),
]

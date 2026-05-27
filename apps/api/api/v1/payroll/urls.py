"""URLs for payroll bounded context.

Legacy payroll API is stubbed during the Vyntia Pay migration (D.1a). A
catch-all routes every /api/v1/payroll/* path + verb to a 501 so frontend
consumers degrade gracefully until each endpoint family is rebuilt
(D.2 config, D.5 runs, D.6 boletas).
"""

from django.urls import re_path

from api.v1.payroll.stub_views import PayrollUnavailableView

app_name = "payroll"

urlpatterns = [
    re_path(r"^.*$", PayrollUnavailableView.as_view(), name="payroll-unavailable"),
]

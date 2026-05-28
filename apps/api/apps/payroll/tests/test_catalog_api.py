"""D.2 — read-only catalog endpoints registered before the legacy 501 catch-all."""

import pytest
from django.core.management import call_command


@pytest.mark.django_db
class TestCatalogApi:
    def test_tax_parameters_list_read_only(self, authenticated_client):
        client, _ = authenticated_client
        call_command("seed_payroll_catalog")
        resp = client.get("/api/v1/payroll/catalog/tax-parameters/")
        assert resp.status_code == 200
        assert client.post("/api/v1/payroll/catalog/tax-parameters/", {}).status_code == 405

    def test_payroll_concepts_filter_by_sunat_code(self, authenticated_client):
        client, _ = authenticated_client
        call_command("seed_payroll_catalog")
        resp = client.get("/api/v1/payroll/catalog/payroll-concepts/?sunat_code=0101")
        assert resp.status_code == 200

    def test_legacy_path_still_501(self, authenticated_client):
        client, _ = authenticated_client
        assert client.get("/api/v1/payroll/monthly-runs/").status_code == 501

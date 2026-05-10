"""Email-template branding regression test (B.5b #33)."""
from pathlib import Path


class TestEmailTemplateBranding:
    def test_no_intranet_strings_in_email_templates(self):
        # apps/api/apps/onboarding/tests/test_email_branding.py
        # parents[4] = apps/api/  → resolve to apps/api/templates/emails/
        templates_dir = Path(__file__).resolve().parents[3] / "templates" / "emails"
        offenders = []
        for path in templates_dir.glob("**/*"):
            if path.is_file() and path.suffix in (".html", ".txt"):
                content = path.read_text(encoding="utf-8")
                if "Intranet" in content:
                    offenders.append(str(path))
        assert offenders == [], (
            f"Templates still contain 'Intranet': {offenders}"
        )

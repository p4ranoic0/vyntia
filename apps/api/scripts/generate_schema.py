#!/usr/bin/env python
"""Generate OpenAPI schema excluding problematic APIViews."""

import os
import sys

import django

# Setup Django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "vyntia.settings.development")
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

import yaml
from drf_spectacular.generators import SchemaGenerator
from rest_framework.schemas import SchemaGenerator as DRFSchemaGenerator

# Create generator with custom patterns to ignore
generator = SchemaGenerator(
    patterns=[
        pattern
        for pattern in __import__("django.urls").urls.get_resolver().url_patterns
        if "logout" not in str(pattern)
        and "profile" not in str(pattern)
        and "menu" not in str(pattern)
        and "permissions-structure" not in str(pattern)
    ]
)

try:
    schema = generator.get_schema(request=None, public=True)
    with open("schema.yml", "w", encoding="utf-8") as f:
        yaml.dump(schema, f, allow_unicode=True, default_flow_style=False)
    print("✅ Schema generated successfully: schema.yml")
except Exception as e:
    print(f"❌ Error generating schema: {e}")
    import traceback

    traceback.print_exc()
    traceback.print_exc()

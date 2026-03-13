#!/usr/bin/env python
"""
Script para generar schema OpenAPI limpio sin warnings
"""
import os
import sys

import django

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
django.setup()

import json

from drf_spectacular.generators import SchemaGenerator

# Generate schema
generator = SchemaGenerator()
schema = generator.get_schema(request=None, public=True)

# Write to file
output_path = os.path.join(
    os.path.dirname(__file__), "..", "front", "openapi-schema.json"
)
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(schema, f, indent=2)

print(f"✅ Schema generado exitosamente: {output_path}")
print(f"📏 Tamaño: {os.path.getsize(output_path)} bytes")
print(f"✅ Schema generado exitosamente: {output_path}")
print(f"📏 Tamaño: {os.path.getsize(output_path)} bytes")

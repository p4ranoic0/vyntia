"""RLS (Row-Level Security) helpers for the tenancy layer.

This package contains:
- policies.py: pure functions that generate SQL strings for RLS policies
- introspection.py: discovery of which Django models are tenant-scoped
"""

"""Cross-cutting constants for the tenancy layer."""

# Reserved subdomains that NEVER resolve to a tenant.
# When the host's subdomain matches one of these, request.tenant = None.
# These also block tenant slugs from being claimed.
RESERVED_SUBDOMAINS = frozenset({
    "admin",       # admin.vyntia.pe — Vyntia staff panel
    "app",         # app.vyntia.pe — workspace switcher
    "www",         # www.vyntia.pe — marketing redirect
    "api",         # api.vyntia.pe — public API alias (future)
    "docs",        # documentation
    "status",      # status page
    "blog",        # blog
    "mail",        # email
    "support",     # support portal
    "help",        # help center
    "vyntia",      # brand-protect

    # Local/dev hosts — treat as no-tenant
    "localhost",
    "127",         # 127.0.0.1
    "0",           # 0.0.0.0
})

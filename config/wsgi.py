import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()

# Auto-run database migrations on WSGI startup (ensures fresh containers have required tables)
try:
    from django.core.management import call_command
    call_command('migrate', interactive=False)
except Exception as e:
    print("Auto-migration on WSGI startup exception:", e)


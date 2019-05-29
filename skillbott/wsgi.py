"""
WSGI config for skillbott project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

sys.path.insert(0, '/var/www/skillbott'.replace('/skillbott', ''))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skillbott.settings')

application = get_wsgi_application()


""" skillbott.conf
<VirtualHost *:9000>
    ErrorLog "/private/var/log/apache2/skillbott-error_log"
    CustomLog "/private/var/log/apache2/skillbott-access_log" common
    
    Alias /static/ /var/www/skillbott/static/
    <Directory /var/www/skillbott/static>
        Require all granted
    </Directory>

    <Directory /var/www/skillbott>
        <Files wsgi.py>
            Require all granted
        </Files>
    </Directory>

    WSGIDaemonProcess skillbott python-path=/var/www/skillbott python-home=/Users/flaniganswake/Projects/skillbott-env
    WSGIProcessGroup skillbott
    WSGIScriptAlias / /var/www/skillbott/wsgi.py
</VirtualHost>
"""

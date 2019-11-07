#!/usr/bin/env bash

pwd

cat <<EOF | python
import os

from bots import botsinit
from django.core.management import execute_from_command_line

botsinit.generalinit('config')

execute_from_command_line(['manage.py', 'makemigrations'])
execute_from_command_line(['manage.py', 'migrate'])

from django.contrib.auth import get_user_model
User = get_user_model()

username = os.environ.get('ADMIN_ACCOUNT', 'admin_')
email = os.environ.get('ADMIN_EMAIL', 'hello@example.com')
password = os.environ.get('ADMIN_PASSWORD', 'prettygoodpassword')

User.objects.filter(username=username).exists() or \
    User.objects.create_superuser(username, email, password)
EOF


/usr/local/bin/supervisord -c /etc/supervisor/supervisord.conf

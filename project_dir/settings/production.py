''' For production we could pull the creds from services like ssm.'''
from pathlib import Path
from datetime import timedelta

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'django-insecure-o=lnduz=jmrs=f(1veql&6h$f=&=z#3&gy+oi$fj*5goyit@lh'

# I chose sqlite3 for the sake of simplicity.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

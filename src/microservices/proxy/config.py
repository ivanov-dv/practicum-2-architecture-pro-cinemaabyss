import os

MONOLITH_URL = os.environ['MONOLITH_URL']
MOVIES_SERVICE_URL = os.environ['MOVIES_SERVICE_URL']
EVENTS_SERVICE_URL = os.environ['EVENTS_SERVICE_URL']

GRADUAL_MIGRATION = os.getenv('GRADUAL_MIGRATION', 'false').lower() in ('1', 'true', 'yes')
MOVIES_MIGRATION_PERCENT = int(os.getenv('MOVIES_MIGRATION_PERCENT', '0'))

UPSTREAM_TIMEOUT = float(os.getenv('UPSTREAM_TIMEOUT', '30'))

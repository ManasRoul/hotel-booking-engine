import sys
import os
import traceback

# Add your project directory to the sys.path
project_home = os.path.dirname(__file__)
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Set up virtual environment
VENV_PATH = os.path.join(project_home, 'venv', 'bin', 'activate_this.py')
if os.path.exists(VENV_PATH):
    exec(open(VENV_PATH).read(), {'__file__': VENV_PATH})
else:
    import site
    import glob
    venv_site = os.path.join(project_home, 'venv', 'lib')
    site_packages = glob.glob(os.path.join(venv_site, 'python*', 'site-packages'))
    if site_packages:
        site.addsitedir(site_packages[0])

# Load environment variables from .env
env_file = os.path.join(project_home, '.env')
if os.path.exists(env_file):
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key.strip()] = value.strip()

# Import Flask app and create tables
try:
    from app import app as application, db
    with application.app_context():
        db.create_all()
except Exception as e:
    print(f"[passenger_wsgi] ERROR: {e}")
    traceback.print_exc()
    raise

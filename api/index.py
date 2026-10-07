import os
import sys

# Ensure backend directory is in path
backend_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.db.database import init_db
try:
    init_db()
except Exception:
    pass

from app.main import app

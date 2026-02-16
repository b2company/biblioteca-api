import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from mangum import Mangum
from backend.main import app

handler = Mangum(app, lifespan="off")

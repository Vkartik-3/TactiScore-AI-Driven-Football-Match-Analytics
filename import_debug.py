import sys
import os

# Print current working directory
print("Current Working Directory:", os.getcwd())

# Add project root to Python path
project_root = os.path.dirname(os.path.abspath('.'))
sys.path.append(project_root)
print("Added Project Root:", project_root)

# Try importing database components
try:
    from database.config import Base, DATABASE_URL
    print("Successfully imported Base and DATABASE_URL")
    print("Base:", Base)
    print("DATABASE_URL:", DATABASE_URL)
except ImportError as e:
    print("Import Error:", e)
    print("Sys Path:", sys.path)
    print("Project Root Contents:", os.listdir(project_root))
    print("Database Directory Contents:", os.listdir(os.path.join(project_root, 'database')))
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)

from shared.database import init_db

if __name__ == "__main__":
    print("Initializing database...")
    try:
        init_db()
        print("✅ Database initialization successful!")
    except Exception as e:
        print(f"❌ Database initialization failed: {str(e)}")

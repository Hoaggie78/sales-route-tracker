import sys
import os
import traceback
from dotenv import load_dotenv

sys.path.append(os.path.join(os.getcwd(), 'backend'))
load_dotenv()

try:
    from app.core.database import init_db
    print("Connecting to Supabase...")
    init_db()
    print("Success! Tables created in Supabase.")
except Exception:
    print("Error initializing database:")
    traceback.print_exc()
    sys.exit(1)

"""
WBS BPKH - Database Factory
Automatically selects SQLite or Supabase based on configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def get_database():
    """
    Get database instance based on DB_MODE environment variable.

    DB_MODE options:
    - 'supabase': Use Supabase cloud database
    - 'sqlite': Use local SQLite database (default)
    """
    db_mode = os.getenv('DB_MODE', 'sqlite').lower()

    if db_mode == 'supabase':
        from database_supabase import SupabaseDatabase
        return SupabaseDatabase()
    else:
        from database import WBSDatabase
        db_path = os.getenv('DB_PATH', 'wbs_database.db')
        return WBSDatabase(db_path)


# Alias for backward compatibility
def WBSDatabase(db_path: str = None):
    """
    Wrapper function for backward compatibility.
    Returns appropriate database based on DB_MODE.
    """
    db_mode = os.getenv('DB_MODE', 'sqlite').lower()

    if db_mode == 'supabase':
        from database_supabase import SupabaseDatabase
        return SupabaseDatabase()
    else:
        from database import WBSDatabase as SQLiteDB
        return SQLiteDB(db_path or os.getenv('DB_PATH', 'wbs_database.db'))

import asyncio
from database import get_supabase_client, initialize_database

async def main():
    """
    Initializes or updates the database schema by calling initialize_database.
    """
    try:
        client = get_supabase_client()
        print("Supabase client initialized.")
        await initialize_database(client)
        print("Database schema has been initialized or updated successfully.")
    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An error occurred during database migration: {e}")

if __name__ == "__main__":
    asyncio.run(main())
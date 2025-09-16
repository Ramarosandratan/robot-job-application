import os
from supabase import create_client, Client
import datetime

# Placeholders for Supabase credentials
SUPABASE_URL = os.environ.get("SUPABASE_URL", "YOUR_SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY", "YOUR_SUPABASE_KEY")

def get_supabase_client() -> Client:
    """Initializes and returns a Supabase client."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise ValueError("Supabase URL and Key must be set in environment variables or replaced in database.py")
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def create_jobs_table(client: Client):
    """Creates the 'jobs' table if it doesn't exist."""
    try:
        # Supabase client doesn't have a direct 'execute_sql' method for DDL.
        # We'll use the postgrest client directly for this.
        # This is a simplified approach; in a real application, you might use a migration tool.
        sql_command = """
        CREATE TABLE IF NOT EXISTS jobs (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            skills TEXT,
            publication_date DATE,
            company_name VARCHAR(255) NOT NULL,
            location VARCHAR(255) NOT NULL,
            application_link VARCHAR(255) UNIQUE NOT NULL,
            relevance_score REAL,
            status VARCHAR(50) DEFAULT 'pending'
        );
        """
        # Note: Direct SQL execution for DDL is not directly exposed via the Python client's
        # standard methods. For creating tables, you typically manage this outside the application
        # (e.g., via Supabase UI, migrations).
        # For demonstration, we'll assume a way to execute raw SQL if needed,
        # but the primary client methods are for data manipulation.
        # As a workaround for this exercise, we'll simulate the table creation.
        # In a real scenario, you'd ensure the table exists via migrations or the Supabase dashboard.
        print("Attempting to create 'jobs' table (or ensuring it exists)...")
        # The Supabase Python client is primarily for data manipulation (CRUD).
        # DDL operations like CREATE TABLE are usually handled via migrations or the Supabase UI.
        # For the purpose of this exercise, we'll acknowledge this limitation and proceed
        # with the assumption that the table creation is handled externally or via a direct
        # database connection if raw SQL is absolutely necessary from Python.
        # Since the prompt specifically asks for a function to "create jobs table",
        # we'll include the SQL, but note the client's typical usage.
        print(f"SQL to create table: {sql_command}")
        print("Please ensure this SQL is executed in your Supabase instance.")

    except Exception as e:
        print(f"Error creating jobs table: {e}")

async def create_applications_table(client: Client):
    """Creates the 'applications' table if it doesn't exist."""
    try:
        sql_command = """
        CREATE TABLE IF NOT EXISTS applications (
            id SERIAL PRIMARY KEY,
            job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            application_date DATE NOT NULL,
            cover_letter_text TEXT,
            cv_link VARCHAR(255),
            status VARCHAR(50) NOT NULL DEFAULT 'sent',
            notes TEXT,
            UNIQUE(job_id, user_id)
        );
        """
        print("Attempting to create 'applications' table (or ensuring it exists)...")
        print(f"SQL to create table: {sql_command}")
        print("Please ensure this SQL is executed in your Supabase instance.")
    except Exception as e:
        print(f"Error creating applications table: {e}")

def save_job_data(client: Client, job_data: dict):
    """
    Saves job data into the 'jobs' table.
    Handles potential duplicate 'application_link' entries by ignoring them.
    """
    try:
        response = client.table('jobs').insert(job_data).execute()
        if response.data:
            print(f"Job data saved successfully: {response.data}")
        elif response.error:
            if "duplicate key value violates unique constraint" in response.error.get("message", ""):
                print(f"Duplicate application_link found, ignoring: {job_data.get('application_link')}")
            else:
                print(f"Error saving job data: {response.error}")
    except Exception as e:
        print(f"An unexpected error occurred while saving job data: {e}")

async def update_job_relevance_score(client: Client, job_id: int, score: float):
    """
    Updates the relevance score for a specific job in the 'jobs' table.
    """
    try:
        response = client.table('jobs').update({'relevance_score': score}).eq('id', job_id).execute()
        if response.data:
            print(f"Job {job_id} relevance score updated to {score}.")
        elif response.error:
            print(f"Error updating relevance score for job {job_id}: {response.error}")
    except Exception as e:
        print(f"An unexpected error occurred while updating job relevance score: {e}")

async def get_user_profile(client: Client, user_id: int):
    """
    Fetches a user's profile information (including preferred job criteria, profile text, summary, skills, and professional links) from the 'users' table.
    """
    try:
        response = await client.table('users').select('preferred_criteria, profile_text, summary, skills, linkedin_link, github_link, portfolio_link').eq('id', user_id).single().execute()
        if response.data:
            print(f"User profile fetched successfully for user_id {user_id}.")
            return response.data
        elif response.error:
            print(f"Error fetching user profile for user_id {user_id}: {response.error}")
            return None
    except Exception as e:
        print(f"An unexpected error occurred while fetching user profile: {e}")
        return None

async def get_unscored_jobs(client: Client):
    """
    Fetches all jobs from the 'jobs' table that have not yet been scored
    (i.e., relevance_score is NULL or 0).
    """
    try:
        response = await client.table('jobs').select('*').or_('relevance_score.is.null,relevance_score.eq.0').execute()
        if response.data:
            print(f"Found {len(response.data)} unscored jobs.")
            return response.data
        elif response.error:
            print(f"Error fetching unscored jobs: {response.error}")
            return []
    except Exception as e:
        print(f"An unexpected error occurred while fetching unscored jobs: {e}")
        return []

async def get_jobs_for_application(client: Client, relevance_threshold: int):
    """
    Retrieves jobs from the 'jobs' table that meet certain criteria for application:
    - relevance_score above a specified threshold
    - status is not 'applied'
    """
    try:
        response = await client.table('jobs').select('*').gte('relevance_score', relevance_threshold).eq('status', 'pending').execute()
        if response.data:
            print(f"Found {len(response.data)} jobs for application with relevance score >= {relevance_threshold}.")
            return response.data
        elif response.error:
            print(f"Error fetching jobs for application: {response.error}")
            return []
    except Exception as e:
        print(f"An unexpected error occurred while fetching jobs for application: {e}")
        return []

async def update_job_status(client: Client, job_id: int, status: str):
    """
    Updates the status for a specific job in the 'jobs' table.
    """
    try:
        response = await client.table('jobs').update({'status': status}).eq('id', job_id).execute()
        if response.data:
            print(f"Job {job_id} status updated to '{status}'.")
        elif response.error:
            print(f"Error updating status for job {job_id}: {response.error}")
    except Exception as e:
        print(f"An unexpected error occurred while updating job status: {e}")
        return None

async def create_users_table(client: Client):
    """Creates the 'users' table if it doesn't exist."""
    try:
        sql_command = """
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(255) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
        );
        """
        print("Attempting to create 'users' table (or ensuring it exists)...")
        print(f"SQL to create table: {sql_command}")
        print("Please ensure this SQL is executed in your Supabase instance.")
    except Exception as e:
        print(f"Error creating users table: {e}")

async def create_skills_table(client: Client):
    """Creates the 'skills' table if it doesn't exist."""
    try:
        sql_command = """
        CREATE TABLE IF NOT EXISTS skills (
            id SERIAL PRIMARY KEY,
            name VARCHAR(255) UNIQUE NOT NULL
        );
        """
        print("Attempting to create 'skills' table (or ensuring it exists)...")
        print(f"SQL to create table: {sql_command}")
        print("Please ensure this SQL is executed in your Supabase instance.")
    except Exception as e:
        print(f"Error creating skills table: {e}")

async def create_user_skills_table(client: Client):
    """Creates the 'user_skills' table if it doesn't exist."""
    try:
        sql_command = """
        CREATE TABLE IF NOT EXISTS user_skills (
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
            PRIMARY KEY (user_id, skill_id)
        );
        """
        print("Attempting to create 'user_skills' table (or ensuring it exists)...")
        print(f"SQL to create table: {sql_command}")
        print("Please ensure this SQL is executed in your Supabase instance.")
    except Exception as e:
        print(f"Error creating user_skills table: {e}")

async def create_job_skills_table(client: Client):
    """Creates the 'job_skills' table if it doesn't exist."""
    try:
        sql_command = """
        CREATE TABLE IF NOT EXISTS job_skills (
            job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
            skill_id INTEGER NOT NULL REFERENCES skills(id) ON DELETE CASCADE,
            PRIMARY KEY (job_id, skill_id)
        );
        """
        print("Attempting to create 'job_skills' table (or ensuring it exists)...")
        print(f"SQL to create table: {sql_command}")
async def save_application_details(client: Client, job_id: int, cover_letter_text: str, user_id: int, cv_link: str = None, status: str = 'sent', notes: str = None):
    """
    Saves application details into the 'applications' table.
    """
    try:
        data = {
            "job_id": job_id,
            "user_id": user_id, # Assuming a default user_id for now, or it should be passed
            "application_date": datetime.date.today().isoformat(),
            "cover_letter_text": cover_letter_text,
            "cv_link": cv_link,
            "status": status,
            "notes": notes
        }
        response = client.table('applications').insert(data).execute()
        if response.data:
            print(f"Application details saved successfully for job_id {job_id}: {response.data}")
            return response.data[0]['id']
        elif response.error:
            print(f"Error saving application details for job_id {job_id}: {response.error}")
            return None
    except Exception as e:
        print(f"An unexpected error occurred while saving application details: {e}")
        return None

        print("Please ensure this SQL is executed in your Supabase instance.")
    except Exception as e:
        print(f"Error creating job_skills table: {e}")
async def is_job_already_scraped(client: Client, application_link: str) -> bool:
    """
    Checks if a job with a given `application_link` already exists in the `jobs` table.

    Args:
        client: The Supabase client.
        application_link (str): The application link of the job.

    Returns:
        bool: True if a job with the application link is found, False otherwise.
    """
    response = await client.from_('jobs').select('id').eq('application_link', application_link).execute()
    if response.data:
        return True
    return False

async def log_application_status(client: Client, application_id: int, status: str, notes: str = None):
    """
    Logs the status of a sent application in the 'applications' table.
    """
    try:
        data = {
            "status": status,
            "notes": notes
        }
        response = client.table('applications').update(data).eq('id', application_id).execute()
        if response.data:
            print(f"Application {application_id} status updated to '{status}'.")
        elif response.error:
            print(f"Error updating status for application {application_id}: {response.error}")
    except Exception as e:
        print(f"An unexpected error occurred while logging application status: {e}")

async def initialize_database(client: Client):
    """Initializes all necessary database tables."""
    print("Initializing database tables...")
    await create_users_table(client)
    await create_skills_table(client)
    await create_jobs_table(client) # jobs table is needed for applications and job_skills
    await create_applications_table(client)
    await create_user_skills_table(client)
    await create_job_skills_table(client)
    print("Database initialization complete.")

if __name__ == "__main__":
    # Example usage (for testing purposes)
    print("Running example usage...")
    import asyncio
    try:
        supabase_client = get_supabase_client()
        print("Supabase client initialized.")

        asyncio.run(initialize_database(supabase_client))

        example_job = {
            "title": "Software Engineer",
            "description": "Develop and maintain software.",
            "skills": "Python, SQL, AWS",
            "publication_date": "2023-01-15",
            "company_name": "Tech Corp",
            "location": "Remote",
            "application_link": "https://example.com/job/123"
        }
        # save_job_data is not async, so it can be called directly
        save_job_data(supabase_client, example_job)

        # Attempt to save a duplicate to test handling
        duplicate_job = {
            "title": "Senior Software Engineer",
            "description": "Lead a team of engineers.",
            "skills": "Python, SQL, AWS, Leadership",
            "publication_date": "2023-01-16",
            "company_name": "Tech Corp",
            "location": "Remote",
            "application_link": "https://example.com/job/123" # Duplicate link
        }
        save_job_data(supabase_client, duplicate_job)

        # Example of saving application details
        # Assuming a user with ID 1 exists for this example
        example_user_id = 1
        example_job_id = 1 # Assuming job with ID 1 exists from previous save_job_data
        example_cover_letter = "Dear Hiring Manager, I am very interested in this role..."
        example_cv_link = "https://example.com/my_cv.pdf"

        print("\nAttempting to save application details...")
        application_id = asyncio.run(save_application_details(
            supabase_client,
            job_id=example_job_id,
            cover_letter_text=example_cover_letter,
            user_id=example_user_id,
            cv_link=example_cv_link,
            status='sent',
            notes='Applied via automated system.'
        ))
        if application_id:
            print(f"New application saved with ID: {application_id}")
        else:
            print("Failed to save application details.")

    except ValueError as ve:
        print(f"Configuration Error: {ve}")
    except Exception as e:
        print(f"An error occurred during example usage: {e}")
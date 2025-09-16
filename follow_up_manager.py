import asyncio
import datetime
from supabase import Client
from email_sender import send_application_email
from database import get_supabase_client # Assuming get_supabase_client is needed for testing or direct use

async def send_follow_up_emails(client: Client, days_since_application: int = 7):
    """
    Fetches applications with 'sent' status older than days_since_application,
    sends follow-up emails, and updates their status to 'followed_up'.

    Args:
        client (Client): The Supabase client instance.
        days_since_application (int): The number of days since application to consider for follow-up.

    Returns:
        list: A list of application IDs for which follow-up emails were sent.
    """
    followed_up_application_ids = []
    
    # Calculate the date threshold
    date_threshold = (datetime.date.today() - datetime.timedelta(days=days_since_application)).isoformat()

    # 1. Fetch applications
    response = await client.table('applications').select('*').eq('status', 'sent').lt('application_date', date_threshold).execute()
    applications_to_follow_up = response.data

    if not applications_to_follow_up:
        print("No applications found for follow-up.")
        return []

    print(f"Found {len(applications_to_follow_up)} applications to follow up.")

    for app in applications_to_follow_up:
        application_id = app['id']
        job_id = app['job_id']
        user_id = app['user_id']

        # 2. Retrieve associated job details
        job_response = await client.table('jobs').select('title, company_name').eq('id', job_id).single().execute()
        job_details = job_response.data

        if not job_details:
            print(f"Could not retrieve job details for job_id {job_id}. Skipping application {application_id}.")
            continue

        job_title = job_details['title']
        company_name = job_details['company_name']

        # Retrieve user email
        user_response = await client.table('users').select('email').eq('id', user_id).single().execute()
        user_email_data = user_response.data

        if not user_email_data:
            print(f"Could not retrieve user email for user_id {user_id}. Skipping application {application_id}.")
            continue
        
        recipient_email = user_email_data['email']

        # 3. Construct a generic follow-up email message
        follow_up_subject = f"Following up on my application for {job_title} at {company_name}"
        follow_up_body = (
            f"Dear Hiring Manager,\n\n"
            f"I hope this email finds you well. I am writing to follow up on my application for the "
            f"{job_title} position at {company_name}, which I submitted on {app['application_date']}.\n\n"
            f"I remain very interested in this opportunity and believe my skills and experience align well with the requirements of this role.\n\n"
            f"Thank you for your time and consideration. I look forward to hearing from you soon.\n\n"
            f"Sincerely,\n[Your Name]" # Placeholder for actual user name
        )

        # 4. Use the send_application_email function
        print(f"Sending follow-up email for application {application_id} to {recipient_email}...")
        email_sent_successfully = await send_application_email(
            recipient_email=recipient_email,
            job_title=job_title,
            company_name=company_name,
            cover_letter_text=follow_up_body, # Using the follow-up body as cover_letter_text
            cv_path=None # No CV for follow-up
        )

        if email_sent_successfully:
            print(f"Follow-up email sent successfully for application {application_id}.")
            # 5. Update the status of the application
            update_response = await client.table('applications').update({'status': 'followed_up'}).eq('id', application_id).execute()
            if update_response.data:
                print(f"Application {application_id} status updated to 'followed_up'.")
                followed_up_application_ids.append(application_id)
            elif update_response.error:
                print(f"Error updating status for application {application_id}: {update_response.error}")
        else:
            print(f"Failed to send follow-up email for application {application_id}.")
    
    return followed_up_application_ids

if __name__ == "__main__":
    async def main():
        try:
            supabase_client = get_supabase_client()
            print("Supabase client initialized for follow-up manager.")
            
            # Example usage: send follow-ups for applications older than 7 days
            # For testing, ensure you have 'applications', 'jobs', and 'users' tables populated
            # with relevant data (status 'sent', application_date, job_id, user_id).
            print("Attempting to send follow-up emails...")
            sent_ids = await send_follow_up_emails(supabase_client, days_since_application=7)
            
            if sent_ids:
                print(f"Successfully sent follow-up emails for application IDs: {sent_ids}")
            else:
                print("No follow-up emails were sent.")

        except ValueError as ve:
            print(f"Configuration Error: {ve}")
        except Exception as e:
            print(f"An error occurred during follow-up manager example usage: {e}")

    # Uncomment the line below to run the example when this script is executed directly
    # asyncio.run(main())
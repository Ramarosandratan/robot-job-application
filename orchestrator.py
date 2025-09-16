import asyncio
import os # Import os for environment variables
from database import get_supabase_client, get_user_profile, save_job_data, update_job_relevance_score, get_unscored_jobs, get_jobs_for_application, save_application_details, update_job_status
from scraper import scrape_jobs_from_search_page
from filter_jobs import filter_jobs
from relevance_scorer import calculate_relevance_score
from application_generator import generate_cover_letter
from follow_up_manager import send_follow_up_emails
from email_sender import send_application_email # Import send_application_email

REPORT_RECIPIENT_EMAIL = os.getenv("REPORT_RECIPIENT_EMAIL")

async def send_report_email(recipient_email: str, subject: str, body: str):
    """
    Sends a general report email using the send_application_email function.
    """
    # Reusing send_application_email, but without job-specific details or CV
    # The job_title and company_name are set to generic values for a report.
    print(f"Attempting to send report email to {recipient_email} with subject: {subject}")
    success = await send_application_email(
        recipient_email=recipient_email,
        job_title=subject, # Using subject as job_title for generic email
        company_name="Daily Report System", # Generic company name
        cover_letter_text=body,
        cv_path=None # No CV for a general report
    )
    if success:
        print(f"Report email sent successfully to {recipient_email}.")
    else:
        print(f"Failed to send report email to {recipient_email}.")
    return success

async def run_daily_scraping(user_id: int, search_url: str, max_pages: int = 5, relevance_threshold: int = 50):
    """
    Orchestrates the daily job scraping, filtering, and saving process for a specific user.
    """
    print(f"Starting daily scraping for user {user_id} with search URL: {search_url}")

    client = get_supabase_client()

    # 1. Scrape raw job data
    print(f"Scraping jobs from {search_url} for {max_pages} pages...")
    raw_jobs = await scrape_jobs_from_search_page(search_url, max_pages)
    jobs_scraped_count = len(raw_jobs)
    print(f"Scraped {jobs_scraped_count} raw jobs.")

    # 2. Fetch user's preferred job criteria and profile text
    print(f"Fetching user profile for user_id {user_id}...")
    user_profile = await get_user_profile(client, user_id)
    if not user_profile:
        print(f"Could not fetch user profile for user_id {user_id}. Aborting scraping.")
        return {"status": "failed", "message": "User profile not found."}

    preferred_criteria = user_profile.get('preferred_criteria', {})
    profile_text = user_profile.get('profile_text', '')
    user_summary = user_profile.get('summary', '')
    user_skills = user_profile.get('skills', [])
    user_linkedin = user_profile.get('linkedin_link', '')
    user_github = user_profile.get('github_link', '')
    user_portfolio = user_profile.get('portfolio_link', '')

    # Reconstruct user_profile for application generation to include all necessary fields
    full_user_profile = {
        "id": user_id,
        "preferred_criteria": preferred_criteria,
        "profile_text": profile_text,
        "summary": user_summary,
        "skills": user_skills,
        "linkedin": user_linkedin,
        "github": user_github,
        "portfolio_link": user_portfolio
    }
    print(f"User preferred criteria: {preferred_criteria}")

    # 3. Filter scraped jobs
    print("Filtering scraped jobs based on user criteria...")
    filtered_jobs = filter_jobs(raw_jobs, preferred_criteria)
    jobs_filtered_count = len(filtered_jobs)
    print(f"Filtered down to {jobs_filtered_count} relevant jobs.")

    relevant_jobs_found = 0
    # 4. Calculate relevance score and save each filtered job
    for job in filtered_jobs:
        print(f"Processing job: {job.get('title')} at {job.get('company_name')}")
        
        # Calculate relevance score
        score = calculate_relevance_score(job, profile_text)
        job['relevance_score'] = score

        # Save job data
        # Assuming save_job_data returns the saved job's ID or a similar identifier
        # and that it handles duplicates based on application_link
        saved_job_response = save_job_data(client, job)
        
        if saved_job_response and saved_job_response.data:
            job_id = saved_job_response.data[0]['id']
            print(f"Job saved with ID: {job_id}. Relevance score: {score}")

            # Update relevance score (if needed, as it's already in the insert, but for explicit update)
            await update_job_relevance_score(client, job_id, score)

            if score >= relevance_threshold:
                relevant_jobs_found += 1
        else:
            print(f"Could not save job: {job.get('application_link')}. It might be a duplicate or an error occurred.")

    # 5. Score any previously unscored jobs
    jobs_scored_count = await score_unscored_jobs(user_id, client)

    # 6. Generate and Save Applications
    print(f"Identifying jobs for application for user {user_id}...")
    application_threshold = relevance_threshold + 10 # A higher threshold for applying
    jobs_to_apply = await get_jobs_for_application(client, application_threshold)
    applications_generated_count = 0

    if jobs_to_apply:
        print(f"Found {len(jobs_to_apply)} jobs meeting application criteria (relevance >= {application_threshold}).")
        for job in jobs_to_apply:
            job_id = job.get('id')
            print(f"Generating application for job {job_id}: {job.get('title')} at {job.get('company_name')}")
            
            # Generate cover letter
            cover_letter = await generate_cover_letter(job, full_user_profile)

            if cover_letter and "Failed to generate cover letter" not in cover_letter:
                # Save application details
                application_id = await save_application_details(
                    client,
                    job_id=job_id,
                    cover_letter_text=cover_letter,
                    user_id=user_id,
                    status='generated' # Status 'generated' before actual sending
                )
                if application_id:
                    print(f"Application generated and saved for job {job_id}. Application ID: {application_id}")
                    await update_job_status(client, job_id, 'applied')
                    applications_generated_count += 1
                else:
                    print(f"Failed to save application details for job {job_id}.")
            else:
                print(f"Skipping application for job {job_id} due to cover letter generation failure.")
    else:
        print("No jobs found meeting application criteria.")

    # 7. Run Follow-up Manager
    print(f"Checking for eligible applications for follow-up for user {user_id}...")
    followed_up_application_ids = await send_follow_up_emails(client)
    follow_up_emails_sent_count = len(followed_up_application_ids)
    print(f"Sent {follow_up_emails_sent_count} follow-up emails for user {user_id}.")

    print(f"Daily scraping and scoring completed for user {user_id}.")

    # 8. Generate and Send Daily Report
    report_message = (
        f"Daily Job Application Report for User {user_id}:\n\n"
        f"Jobs Scraped: {jobs_scraped_count}\n"
        f"Jobs Filtered: {jobs_filtered_count}\n"
        f"Relevant Jobs Found (score >= {relevance_threshold}): {relevant_jobs_found}\n"
        f"Jobs Scored in Batch: {jobs_scored_count}\n"
        f"Applications Generated: {applications_generated_count}\n"
        f"Follow-up Emails Sent: {follow_up_emails_sent_count}\n\n"
        f"Search URL: {search_url}"
    )
    
    report_sent = False
    if REPORT_RECIPIENT_EMAIL:
        print(f"Generating and sending daily report to {REPORT_RECIPIENT_EMAIL}...")
        report_sent = await send_report_email(
            recipient_email=REPORT_RECIPIENT_EMAIL,
            subject=f"Daily Job Application Report - User {user_id}",
            body=report_message
        )
    else:
        print("REPORT_RECIPIENT_EMAIL not set. Skipping daily report.")

    return {
        "status": "success",
        "user_id": user_id,
        "search_url": search_url,
        "jobs_scraped": jobs_scraped_count,
        "jobs_filtered": jobs_filtered_count,
        "relevant_jobs_found": relevant_jobs_found,
        "jobs_scored_in_batch": jobs_scored_count,
        "relevance_threshold": relevance_threshold,
        "applications_generated": applications_generated_count,
        "follow_up_emails_sent": follow_up_emails_sent_count,
        "daily_report_sent": report_sent # New field to indicate if report was sent
    }

async def score_unscored_jobs(user_id: int, client):
    """
    Fetches unscored jobs and calculates/updates their relevance scores.
    """
    print(f"Starting scoring for unscored jobs for user {user_id}.")
    
    # 1. Fetch user profile
    user_profile = await get_user_profile(client, user_id)
    if not user_profile:
        print(f"Could not fetch user profile for user_id {user_id}. Aborting scoring.")
        return 0
    
    profile_text = user_profile.get('profile_text', '')
    if not profile_text:
        print(f"User profile text is empty for user_id {user_id}. Aborting scoring.")
        return 0

    # 2. Fetch unscored jobs
    unscored_jobs = await get_unscored_jobs(client)
    jobs_to_score_count = len(unscored_jobs)
    print(f"Found {jobs_to_score_count} unscored jobs to process.")

    jobs_scored_count = 0
    # 3. Calculate and Store Scores
    for job in unscored_jobs:
        job_id = job.get('id')
        job_description = job.get('description', '')
        
        if not job_description:
            print(f"Job {job_id} has no description, skipping scoring.")
            continue

        print(f"Scoring job {job_id}: {job.get('title')} at {job.get('company_name')}")
        score = calculate_relevance_score(job_description, profile_text)
        await update_job_relevance_score(client, job_id, score)
        jobs_scored_count += 1
    
    print(f"Completed scoring for {jobs_scored_count} jobs for user {user_id}.")
    return jobs_scored_count

if __name__ == "__main__":
    # Example usage for testing
    # Replace with actual user_id and search_url for testing
    example_user_id = 1
    example_search_url = "https://www.linkedin.com/jobs/search/?keywords=software%20engineer"
    
    print(f"Running example daily scraping for user {example_user_id}...")
    summary = asyncio.run(run_daily_scraping(example_user_id, example_search_url, max_pages=1, relevance_threshold=60))
    print("\nScraping Summary:")
    print(summary)
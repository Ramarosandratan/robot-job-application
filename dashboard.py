import streamlit as st
import pandas as pd
import asyncio
from database import get_supabase_client

def get_all_jobs(client):
    """
    Fetches all job entries from the 'jobs' table in the Supabase database.
    """
    try:
        response = client.from_('jobs').select('*').execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching jobs: {e}")
        return []

async def get_all_applications(client):
    """
    Fetches all application entries from the 'applications' table in the Supabase database.
    """
    try:
        response = await client.from_('applications').select('*').execute()
        return response.data
    except Exception as e:
        st.error(f"Error fetching applications: {e}")
        return []

def main():
    st.title("Job Offers Dashboard")

    supabase_client = get_supabase_client()
    if supabase_client:
        jobs_data = get_all_jobs(supabase_client)
        if jobs_data:
            st.subheader("Found Job Offers")
            df = pd.DataFrame(jobs_data)
            # Select and reorder columns for display
            display_columns = [
                'title', 'company_name', 'location', 'publication_date',
                'relevance_score', 'application_link'
            ]
            # Ensure all display_columns exist in the DataFrame
            existing_columns = [col for col in display_columns if col in df.columns]
            df_display = df[existing_columns]

            st.dataframe(df_display)
        else:
            st.info("No job offers found.")

        st.subheader("Sent Applications")
        applications_data = asyncio.run(get_all_applications(supabase_client))
        if applications_data:
            df_applications = pd.DataFrame(applications_data)
            application_display_columns = [
                'job_id', 'application_date', 'status', 'cover_letter_link', 'cv_link'
            ]
            existing_application_columns = [col for col in application_display_columns if col in df_applications.columns]
            st.dataframe(df_applications[existing_application_columns])
        else:
            st.info("No applications found.")

        st.subheader("Application Statistics")
        if jobs_data or applications_data:
            # Number of relevant offers found
            df_jobs = pd.DataFrame(jobs_data)
            relevant_offers_count = df_jobs[df_jobs['relevance_score'] > 50].shape[0]
            st.write(f"**Number of relevant offers found:** {relevant_offers_count}")

            # Number of applications sent
            df_applications = pd.DataFrame(applications_data)
            applications_sent_count = df_applications.shape[0]
            st.write(f"**Number of applications sent:** {applications_sent_count}")

            # Response rate
            if applications_sent_count > 0:
                responded_applications_count = df_applications[
                    df_applications['status'].isin(['interview', 'accepted'])
                ].shape[0]
                response_rate = (responded_applications_count / applications_sent_count) * 100
                st.write(f"**Response rate:** {response_rate:.2f}%")
            else:
                st.write("**Response rate:** N/A (No applications sent)")

            # Breakdown of application statuses (already done, but ensure it's presented clearly as part of the stats)
            st.subheader("Application Status Overview")
            if applications_data:
                # Analyze the 'status' column
                status_counts = df_applications['status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']

                st.write("### Application Status Summary")
                st.dataframe(status_counts)

                st.write("### Application Status Distribution")
                st.bar_chart(status_counts.set_index('Status'))
            else:
                st.info("No applications to analyze for status overview.")
        else:
            st.info("No data available to calculate statistics.")

    else:
        st.error("Failed to connect to Supabase. Please check your database configuration.")

if __name__ == "__main__":
    main()
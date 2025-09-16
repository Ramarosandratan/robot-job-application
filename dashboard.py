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

import asyncio
import streamlit as st
import pandas as pd
from database import get_supabase_client
import application_generator
from datetime import date

def main():
    st.title("Job Offers Dashboard")

    # Create tabs for dashboard sections
    tab1, tab2, tab3 = st.tabs(["Job Applications", "Manage CV", "Statistics"])

    supabase_client = get_supabase_client()
    if not supabase_client:
        st.error("Failed to connect to Supabase. Please check your database configuration.")
        return

    with tab1:
        # Job Offers section
        jobs_data = get_all_jobs(supabase_client)
        if jobs_data:
            st.subheader("Found Job Offers")
            df = pd.DataFrame(jobs_data)
            display_columns = [
                'title', 'company_name', 'location', 'publication_date',
                'relevance_score', 'application_link'
            ]
            existing_columns = [col for col in display_columns if col in df.columns]
            df_display = df[existing_columns]
            st.dataframe(df_display)
        else:
            st.info("No job offers found.")

        # Sent Applications section
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

    with tab2:
        st.header("Manage CV Sections")
        user_id = 1  # TODO: Replace with actual user ID from authentication
        
        # Form for adding new CV sections
        with st.form("cv_section_form"):
            col1, col2 = st.columns(2)
            with col1:
                section_type = st.selectbox("Section Type",
                                          ["Summary", "Experience", "Project", "Education", "Skills"],
                                          index=1)
            with col2:
                start_date = st.date_input("Start Date", value=date.today())
                end_date = st.date_input("End Date", value=date.today())
            
            content = st.text_area("Content", height=200,
                                 placeholder="Describe your experience, responsibilities, and achievements...")
            
            submitted = st.form_submit_button("Save Section")
            if submitted:
                # Format date range
                date_range = f"{start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')}"
                full_content = f"{date_range}\n{content}"
                
                # Update CV section
                asyncio.run(application_generator.update_cv_section(
                    section_type.lower(),
                    full_content,
                    user_id
                ))
                st.success("CV section updated successfully!")
        
        # CV Preview
        st.subheader("Latest CV Preview")
        cv_text, _ = asyncio.run(application_generator.generate_cv(user_id))
        st.markdown(cv_text, unsafe_allow_html=True)
        
        # Version History
        st.subheader("Version History")
        # Get version history from database
        client = get_supabase_client()
        response = client.table('cv_versions') \
            .select('section_type, version, created_at') \
            .eq('user_id', user_id) \
            .order('created_at', desc=True) \
            .execute()
        
        if response.data:
            history_df = pd.DataFrame(response.data)
            st.dataframe(history_df)
        else:
            st.info("No version history available.")

    with tab3:
        # Application Statistics section
        jobs_data = get_all_jobs(supabase_client)
        applications_data = asyncio.run(get_all_applications(supabase_client))
        
        if jobs_data or applications_data:
            st.subheader("Application Statistics")
            
            # Number of relevant offers found
            if jobs_data:
                df_jobs = pd.DataFrame(jobs_data)
                relevant_offers_count = df_jobs[df_jobs['relevance_score'] > 50].shape[0]
                st.write(f"**Number of relevant offers found:** {relevant_offers_count}")
            else:
                st.write("**Number of relevant offers found:** 0")
            
            # Number of applications sent
            if applications_data:
                df_applications = pd.DataFrame(applications_data)
                applications_sent_count = df_applications.shape[0]
                st.write(f"**Number of applications sent:** {applications_sent_count}")
            else:
                st.write("**Number of applications sent:** 0")
            
            # Response rate
            if applications_data and applications_sent_count > 0:
                responded_applications_count = df_applications[
                    df_applications['status'].isin(['interview', 'accepted'])
                ].shape[0]
                response_rate = (responded_applications_count / applications_sent_count) * 100
                st.write(f"**Response rate:** {response_rate:.2f}%")
            else:
                st.write("**Response rate:** N/A (No applications sent)")

            # Application Status Overview
            if applications_data:
                st.subheader("Application Status Overview")
                status_counts = df_applications['status'].value_counts().reset_index()
                status_counts.columns = ['Status', 'Count']
                
                col1, col2 = st.columns(2)
                with col1:
                    st.write("### Status Summary")
                    st.dataframe(status_counts)
                with col2:
                    st.write("### Status Distribution")
                    st.bar_chart(status_counts.set_index('Status'))
        else:
            st.info("No data available to calculate statistics.")

if __name__ == "__main__":
    main()
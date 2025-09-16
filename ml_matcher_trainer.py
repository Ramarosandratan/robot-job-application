import asyncio
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from database import get_supabase_client # Assuming database.py has get_supabase_client

async def train_matching_model(client):
    """
    Trains a machine learning model on historical job and application data
    to improve job matching.

    Args:
        client: The Supabase client.

    Returns:
        str: The path to the saved model.
    """
    # 1. Fetch historical job data
    jobs_response = await client.from_('jobs').select('description, skills').execute()
    jobs_data = jobs_response.data

    # 2. Fetch application data
    applications_response = await client.from_('applications').select('job_id, status, relevance_score').execute()
    applications_data = applications_response.data

    if not jobs_data or not applications_data:
        print("Not enough data to train the model.")
        return None

    jobs_df = pd.DataFrame(jobs_data)
    applications_df = pd.DataFrame(applications_data)

    # Preprocessing: Combine job description and skills
    jobs_df['combined_features'] = jobs_df['description'] + ' ' + jobs_df['skills'].apply(lambda x: ' '.join(x) if isinstance(x, list) else x)

    # Merge dataframes
    # Assuming 'job_id' exists in applications_df and can be used to link to jobs_df
    # For now, let's assume we can link applications to job descriptions directly for simplicity
    # In a real scenario, you'd need to join on a common job identifier.
    # For this example, we'll create a dummy merge or assume applications_df already has job details
    # Let's simplify and assume applications_df has a 'job_description' and 'job_skills' for now
    # This part needs refinement based on actual schema.
    # For now, let's create a simplified dataset for training.

    # For demonstration, let's create a dummy combined feature for applications
    # In a real scenario, you'd join applications with jobs on job_id
    # and then use the job's combined_features.
    # Since we don't have job_id in jobs_df from the select, let's assume a direct link for now.
    # This is a placeholder and needs to be adjusted based on the actual Supabase schema.

    # Let's assume a simplified scenario where we are training on job descriptions
    # and predicting a relevance score.
    # This will require a proper join operation.

    # Placeholder for actual data preparation
    # For now, let's create a dummy dataset for demonstration purposes
    # In a real scenario, you would join applications_df with jobs_df on a common ID.
    # For this example, we'll use a simplified approach.

    # Let's assume 'applications_df' has a 'job_description' column for simplicity
    # and 'relevance_score' as the target.
    # If 'relevance_score' is not available, we'd derive it from 'status'.

    # Example of deriving target variable if relevance_score is not present
    if 'relevance_score' not in applications_df.columns:
        applications_df['relevance_score'] = applications_df['status'].apply(
            lambda x: 1 if x in ['interview', 'accepted'] else 0
        )

    # For now, let's use job descriptions from jobs_df and a dummy target
    # This needs to be properly linked with applications.
    # Let's assume a simplified scenario where we train on job descriptions
    # and predict a binary outcome based on application status.

    # To properly link, we need a common identifier.
    # Let's assume 'jobs' table has an 'id' and 'applications' table has a 'job_id'.
    # Re-fetching with 'id' for jobs.
    jobs_response_with_id = await client.from_('jobs').select('id, description, skills').execute()
    jobs_data_with_id = jobs_response_with_id.data
    jobs_df_with_id = pd.DataFrame(jobs_data_with_id)
    jobs_df_with_id['combined_features'] = jobs_df_with_id['description'] + ' ' + jobs_df_with_id['skills'].apply(lambda x: ' '.join(x) if isinstance(x, list) else x)

    # Merge applications with jobs
    merged_df = pd.merge(applications_df, jobs_df_with_id, left_on='job_id', right_on='id', how='inner')

    if merged_df.empty:
        print("Merged dataframe is empty. Cannot train model.")
        return None

    # Use combined features from the merged dataframe
    X = merged_df['combined_features']
    y = merged_df['relevance_score']

    # TF-IDF Vectorization (reusing logic from ai_matcher.py if available)
    # For now, we'll create a new TfidfVectorizer.
    # In a real scenario, you might want to save/load the vectorizer or ensure consistency.
    vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
    X_vectorized = vectorizer.fit_transform(X)

    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X_vectorized, y, test_size=0.2, random_state=42)

    # Train a simple machine learning model
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)

    # Save the trained model
    model_path = 'job_matching_model.joblib'
    joblib.dump(model, model_path)

    # Save the vectorizer as well, so it can be reused for predictions
    vectorizer_path = 'tfidf_vectorizer.joblib'
    joblib.dump(vectorizer, vectorizer_path)

    print(f"Model trained and saved to {model_path}")
    print(f"Vectorizer saved to {vectorizer_path}")

    return model_path

if __name__ == "__main__":
    async def main():
        client = get_supabase_client()
        model_path = await train_matching_model(client)
        if model_path:
            print(f"Training complete. Model saved at: {model_path}")
        else:
            print("Model training failed.")

    asyncio.run(main())
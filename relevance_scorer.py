from ai_matcher import match_job_to_user

def calculate_relevance_score(job_description: str, user_profile_text: str) -> float:
    """
    Calculates a relevance score between a job description and a user profile.

    Args:
        job_description (str): The text of the job description.
        user_profile_text (str): The text of the user's profile.

    Returns:
        float: The scaled relevance score between 0 and 100.
    """
    cosine_similarity = match_job_to_user(job_description, user_profile_text)
    relevance_score = cosine_similarity * 100
    return relevance_score
import re
from collections import Counter
from ai_matcher import preprocess_text # Reusing preprocess_text from ai_matcher.py
import nltk

# Ensure NLTK stop words are downloaded if not already
try:
    nltk.data.find('corpora/stopwords')
except nltk.downloader.DownloadError:
    nltk.download('stopwords')
try:
    nltk.data.find('tokenizers/punkt')
except nltk.downloader.DownloadError:
    nltk.download('punkt')

def analyze_demanded_technologies(client, num_top_technologies=10):
    """
    Analyzes job descriptions and skills from the 'jobs' table to identify
    the most demanded technologies.

    Args:
        client: The Supabase client instance.
        num_top_technologies (int): The number of top technologies to return.

    Returns:
        list: A list of tuples, where each tuple contains (technology_keyword, count).
    """
    # 1. Fetch all job descriptions and skills from the `jobs` table
    response = client.from_('jobs').select('description, skills').execute()
    jobs_data = response.data

    if not jobs_data:
        return []

    combined_texts = []
    for job in jobs_data:
        description = job.get('description', '')
        skills = job.get('skills', '') # Assuming skills are stored as a string or list of strings

        # 3. Combines the text from job descriptions and extracted skills for each job.
        # If skills is a list, join them into a string
        if isinstance(skills, list):
            combined_text = f"{description} {' '.join(skills)}"
        else:
            combined_text = f"{description} {skills}"
        combined_texts.append(combined_text)

    all_processed_tokens = []
    for text in combined_texts:
        # 4. Performs text analysis (e.g., tokenization, lowercasing, removing stop words)
        #    to identify individual technology keywords.
        processed_text = preprocess_text(text)
        all_processed_tokens.extend(processed_text.split())

    # 5. Counts the frequency of each technology keyword.
    technology_counts = Counter(all_processed_tokens)

    # 6. Returns a list of the top `num_top_technologies` most demanded technologies,
    #    along with their counts.
    return technology_counts.most_common(num_top_technologies)

if __name__ == '__main__':
    # This is a placeholder for a Supabase client.
    # In a real application, you would initialize your Supabase client here.
    class MockSupabaseClient:
        def from_(self, table_name):
            self.table_name = table_name
            return self

        def select(self, columns):
            self.columns = columns
            return self

        def execute(self):
            # Mock data for demonstration
            return {
                "data": [
                    {"description": "Looking for a Python developer with Django and React experience.", "skills": ["Python", "Django", "React", "SQL"]},
                    {"description": "Frontend engineer needed, strong in JavaScript, HTML, CSS, and Vue.js.", "skills": ["JavaScript", "HTML", "CSS", "Vue.js"]},
                    {"description": "Data Scientist with Python, R, and machine learning expertise.", "skills": ["Python", "R", "Machine Learning", "TensorFlow"]},
                    {"description": "DevOps engineer with AWS, Docker, and Kubernetes skills.", "skills": ["AWS", "Docker", "Kubernetes", "CI/CD"]},
                    {"description": "Fullstack developer, proficient in Node.js, Express, and MongoDB.", "skills": ["Node.js", "Express", "MongoDB", "JavaScript"]},
                    {"description": "Seeking a Python developer for backend services.", "skills": ["Python", "Flask"]},
                ]
            }

    mock_client = MockSupabaseClient()
    top_technologies = analyze_demanded_technologies(mock_client, num_top_technologies=5)
    print("Top 5 demanded technologies:")
    for tech, count in top_technologies:
        print(f"- {tech}: {count}")

    print("\nTop 3 demanded technologies:")
    top_3_technologies = analyze_demanded_technologies(mock_client, num_top_technologies=3)
    for tech, count in top_3_technologies:
        print(f"- {tech}: {count}")
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import nltk

# Ensure NLTK stop words are downloaded
try:
    stopwords.words('english')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

def preprocess_text(text):
    """
    A helper function to clean and tokenize text (e.g., lowercase, remove punctuation, stop words).
    """
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)  # Remove punctuation and numbers
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [word for word in tokens if word not in stop_words]
    return " ".join(filtered_tokens)

def generate_tfidf_vectors(documents):
    """
    Takes a list of text documents and generates TF-IDF vectors.
    """
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(documents)
    return tfidf_matrix, vectorizer

def calculate_similarity(vector1, vector2):
    """
    Takes two TF-IDF vectors and calculates their cosine similarity.
    """
    # Reshape vectors for cosine_similarity if they are single samples
    if vector1.ndim == 1:
        vector1 = vector1.reshape(1, -1)
    if vector2.ndim == 1:
        vector2 = vector2.reshape(1, -1)
    
    return cosine_similarity(vector1, vector2)[0][0]

def match_job_to_user(job_description, user_profile_text):
    """
    This main function should:
    *   Take a job_description (string) and user_profile_text (string) as input.
    *   Preprocess both texts.
    *   Generate TF-IDF vectors for both texts.
    *   Calculate the cosine similarity between the two vectors.
    *   Return the similarity score (a float between 0 and 1).
    """
    preprocessed_job = preprocess_text(job_description)
    preprocessed_user = preprocess_text(user_profile_text)

    documents = [preprocessed_job, preprocessed_user]
    tfidf_matrix, vectorizer = generate_tfidf_vectors(documents)

    job_vector = tfidf_matrix[0]
    user_vector = tfidf_matrix[1]

    similarity_score = calculate_similarity(job_vector, user_vector)
    return similarity_score

if __name__ == '__main__':
    # Example Usage
    job_desc = "We are looking for a software engineer with strong Python skills and experience in machine learning."
    user_profile = "I am a Python developer with expertise in data science and machine learning algorithms."

    score = match_job_to_user(job_desc, user_profile)
    print(f"Similarity score: {score}")

    job_desc_2 = "Seeking a marketing specialist with experience in digital campaigns and social media management."
    user_profile_2 = "I am a software engineer specializing in backend development."

    score_2 = match_job_to_user(job_desc_2, user_profile_2)
    print(f"Similarity score (low): {score_2}")
import re

def filter_jobs(job_data, criteria):
    """
    Filters a list of job dictionaries based on user-defined criteria.

    Args:
        job_data (list): A list of dictionaries, where each dictionary represents a job posting.
                         Expected keys: 'location', 'job_duration', 'description', 'skills'.
        criteria (dict): A dictionary of user preferences.
                         Expected keys: 'location_preferences', 'job_duration',
                         'technologies_keywords', 'preferred_languages'.

    Returns:
        list: A list of job dictionaries that match all the specified criteria.
    """
    filtered_jobs = []

    for job in job_data:
        # 1. Location Filter
        location_match = False
        if 'location_preferences' in criteria and criteria['location_preferences']:
            for pref_loc in criteria['location_preferences']:
                if pref_loc.lower() in job.get('location', '').lower():
                    location_match = True
                    break
        else:
            location_match = True # No location criteria, so it's a match

        if not location_match:
            continue

        # 2. Job Duration Filter
        duration_match = False
        if 'job_duration' in criteria and criteria['job_duration']:
            if criteria['job_duration'].lower() in job.get('job_duration', '').lower():
                duration_match = True
        else:
            duration_match = True # No duration criteria, so it's a match

        if not duration_match:
            continue

        # 3. Technologies/Keywords Filter
        tech_keyword_match = False
        if 'technologies_keywords' in criteria and criteria['technologies_keywords']:
            description_skills = (job.get('description', '') + ' ' + job.get('skills', '')).lower()
            for keyword in criteria['technologies_keywords']:
                # Use regex for flexible matching (e.g., "Python" should match "python", "Pythonic", etc.)
                if re.search(r'\b' + re.escape(keyword.lower()) + r'\w*', description_skills):
                    tech_keyword_match = True
                    break
        else:
            tech_keyword_match = True # No tech/keyword criteria, so it's a match

        if not tech_keyword_match:
            continue

        # 4. Preferred Languages Filter
        language_match = False
        if 'preferred_languages' in criteria and criteria['preferred_languages']:
            description_skills = (job.get('description', '') + ' ' + job.get('skills', '')).lower()
            for lang in criteria['preferred_languages']:
                # Use regex for flexible matching
                if re.search(r'\b' + re.escape(lang.lower()) + r'\b', description_skills):
                    language_match = True
                    break
        else:
            language_match = True # No language criteria, so it's a match

        if language_match:
            filtered_jobs.append(job)

    return filtered_jobs

if __name__ == '__main__':
    # Example Usage:
    sample_job_data = [
        {
            'title': 'Software Engineer',
            'location': 'Remote, USA',
            'job_duration': 'Full-time',
            'description': 'Seeking a Python developer with experience in Django and Flask.',
            'skills': 'Python, Django, Flask, AWS'
        },
        {
            'title': 'Frontend Developer',
            'location': 'New York, USA',
            'job_duration': 'Contract',
            'description': 'React and JavaScript experience required. Knowledge of TypeScript is a plus.',
            'skills': 'JavaScript, React, HTML, CSS'
        },
        {
            'title': 'Data Scientist',
            'location': 'London, UK',
            'job_duration': 'Full-time',
            'description': 'Experience with R and machine learning models.',
            'skills': 'R, Machine Learning, SQL'
        },
        {
            'title': 'DevOps Engineer',
            'location': 'Remote, Europe',
            'job_duration': 'Full-time',
            'description': 'Kubernetes, Docker, and Python scripting.',
            'skills': 'Kubernetes, Docker, Python, CI/CD'
        }
    ]

    user_criteria = {
        'location_preferences': ['Remote', 'London'],
        'job_duration': 'Full-time',
        'technologies_keywords': ['Python', 'Django'],
        'preferred_languages': ['English'] # This is a placeholder, as 'English' is not typically in skills/description for programming languages
    }

    filtered_results = filter_jobs(sample_job_data, user_criteria)
    print("Filtered Jobs:")
    for job in filtered_results:
        print(f"- {job['title']} ({job['location']})")

    user_criteria_2 = {
        'location_preferences': ['New York'],
        'job_duration': 'Contract',
        'technologies_keywords': ['React'],
        'preferred_languages': []
    }
    filtered_results_2 = filter_jobs(sample_job_data, user_criteria_2)
    print("\nFiltered Jobs (Criteria 2):")
    for job in filtered_results_2:
        print(f"- {job['title']} ({job['location']})")

    user_criteria_3 = {
        'location_preferences': [],
        'job_duration': 'Full-time',
        'technologies_keywords': ['Kubernetes'],
        'preferred_languages': []
    }
    filtered_results_3 = filter_jobs(sample_job_data, user_criteria_3)
    print("\nFiltered Jobs (Criteria 3):")
    for job in filtered_results_3:
        print(f"- {job['title']} ({job['location']})")
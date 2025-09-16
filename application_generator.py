import os
import openai
from dotenv import load_dotenv

load_dotenv()

async def generate_cover_letter(job_data: dict, user_profile: dict) -> str:
    """
    Generates a personalized cover letter based on job data and user profile.

    Args:
        job_data (dict): A dictionary containing job details from the jobs table.
        user_profile (dict): A dictionary containing user details from the users table.

    Returns:
        str: The generated cover letter text.
    """
    openai.api_key = os.getenv("OPENAI_API_KEY")

    if not openai.api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables.")

    # Construct the detailed AI prompt
    prompt = f"""
    You are an AI assistant specialized in writing compelling cover letters.
    Generate a personalized cover letter for the following job application.

    Job Details:
    Title: {job_data.get('title', 'N/A')}
    Company: {job_data.get('company', 'N/A')}
    Location: {job_data.get('location', 'N/A')}
    Description: {job_data.get('description', 'N/A')}
    Requirements: {job_data.get('requirements', 'N/A')}
    Responsibilities: {job_data.get('responsibilities', 'N/A')}

    User Profile:
    Name: {user_profile.get('name', 'N/A')}
    Email: {user_profile.get('email', 'N/A')}
    Phone: {user_profile.get('phone', 'N/A')}
    LinkedIn: {user_profile.get('linkedin', 'N/A')}
    Portfolio: {user_profile.get('portfolio_link', 'N/A')}
    GitHub: {user_profile.get('github_link', 'N/A')}
    Skills: {', '.join(user_profile.get('skills', []))}
    Experience: {user_profile.get('experience', 'N/A')}
    Education: {user_profile.get('education', 'N/A')}
    Summary: {user_profile.get('summary', 'N/A')}

    Please write a professional and engaging cover letter, highlighting how the user's skills and experience
    match the job requirements and responsibilities. The cover letter should be concise,
    well-structured, and persuasive.
    Ensure to naturally integrate the user's professional links (LinkedIn, Portfolio, GitHub) into the closing section of the cover letter.
    """

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4",  # Or another suitable model like "gpt-3.5-turbo"
            messages=[
                {"role": "system", "content": "You are a helpful assistant that writes professional cover letters."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        cover_letter = response.choices[0].message['content'].strip()
        return cover_letter
    except Exception as e:
        print(f"Error generating cover letter: {e}")
        return f"Failed to generate cover letter: {e}"

if __name__ == "__main__":
    # Example usage (for testing purposes)
    import asyncio

    async def main():
        example_job_data = {
            "title": "Software Engineer",
            "company": "Tech Innovations Inc.",
            "location": "San Francisco, CA",
            "description": "We are looking for a talented Software Engineer to join our dynamic team...",
            "requirements": "Proficiency in Python, JavaScript, and cloud platforms. 3+ years of experience.",
            "responsibilities": "Develop and maintain web applications, collaborate with cross-functional teams."
        }

        example_user_profile = {
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "phone": "555-123-4567",
            "linkedin": "linkedin.com/in/janedoe",
            "portfolio_link": "janedoe.com/portfolio",
            "github_link": "github.com/janedoe",
            "skills": ["Python", "JavaScript", "AWS", "React", "SQL"],
            "experience": "3 years as a Full Stack Developer at Innovate Solutions.",
            "education": "M.Sc. Computer Science, University of Example",
            "summary": "Highly motivated software engineer with a passion for building scalable web applications."
        }

        # Set a dummy API key for local testing if not already set in .env
        os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY", "YOUR_DUMMY_API_KEY_HERE")

        if os.getenv("OPENAI_API_KEY") == "YOUR_DUMMY_API_KEY_HERE":
            print("Warning: Using a dummy API key. Please set OPENAI_API_KEY in your .env file for actual AI calls.")

        generated_letter = await generate_cover_letter(example_job_data, example_user_profile)
        print("\n--- Generated Cover Letter ---")
        print(generated_letter)
        print("------------------------------")

    asyncio.run(main())
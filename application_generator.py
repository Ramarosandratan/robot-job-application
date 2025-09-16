import os
import openai
import asyncio
from dotenv import load_dotenv
from database import get_supabase_client
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import io

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

async def update_cv_section(section_type: str, new_content: str, user_id: int) -> None:
    """
    Updates a section of the CV and saves it as a new version in the database.

    Args:
        section_type (str): Type of CV section (e.g., 'summary', 'experience')
        new_content (str): New content for the section
        user_id (int): ID of the user
    """
    client = get_supabase_client()
    
    # Get current max version for this user and section
    response = client.table('cv_versions') \
        .select('version') \
        .eq('user_id', user_id) \
        .eq('section_type', section_type) \
        .order('version', desc=True) \
        .limit(1) \
        .execute()
    
    next_version = 1
    if response.data and len(response.data) > 0:
        next_version = response.data[0]['version'] + 1
    
    # Insert new version
    new_record = {
        'user_id': user_id,
        'section_type': section_type,
        'content': new_content,
        'version': next_version
    }
    client.table('cv_versions').insert(new_record).execute()

def _generate_cv_pdf(cv_text: str) -> bytes:
    """
    Generates a PDF from CV text using ReportLab.

    Args:
        cv_text (str): Formatted CV text

    Returns:
        bytes: PDF content as bytes
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    
    # Split text into paragraphs and create PDF elements
    paragraphs = []
    for line in cv_text.split('\n'):
        if line.strip():
            paragraphs.append(Paragraph(line.strip(), styles['BodyText']))
    
    doc.build(paragraphs)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    return pdf_bytes

async def generate_cv(user_id: int) -> tuple:
    """
    Generates CV text and PDF using the latest versions of all sections.

    Args:
        user_id (int): ID of the user

    Returns:
        tuple: (cv_text: str, pdf_bytes: bytes)
    """
    client = get_supabase_client()
    
    # Get distinct section types for the user
    response = client.table('cv_versions') \
        .select('section_type') \
        .eq('user_id', user_id) \
        .execute()
    
    section_types = {record['section_type'] for record in response.data}
    
    # Get latest version for each section
    sections = {}
    for section_type in section_types:
        response = client.table('cv_versions') \
            .select('content') \
            .eq('user_id', user_id) \
            .eq('section_type', section_type) \
            .order('version', desc=True) \
            .limit(1) \
            .execute()
        
        if response.data:
            sections[section_type] = response.data[0]['content']
    
    # Order sections logically
    preferred_order = ['summary', 'experience', 'education', 'skills']
    ordered_sections = []
    other_sections = []
    
    for section_type, content in sections.items():
        if section_type in preferred_order:
            index = preferred_order.index(section_type)
            ordered_sections.append((index, section_type, content))
        else:
            other_sections.append((len(preferred_order), section_type, content))
    
    all_sections = sorted(ordered_sections + other_sections, key=lambda x: x[0])
    
    # Build CV text
    cv_text = ""
    for _, section_type, content in all_sections:
        cv_text += f"### {section_type.capitalize()}\n{content}\n\n"
    
    # Generate PDF
    pdf_bytes = _generate_cv_pdf(cv_text)
    
    return cv_text, pdf_bytes

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
        
        # Test CV functionality
        user_id = 1
        await update_cv_section('summary', 'Experienced software engineer with 5+ years in web development', user_id)
        await update_cv_section('experience', 'Senior Developer at ABC Corp (2020-present)', user_id)
        cv_text, pdf_bytes = await generate_cv(user_id)
        print("\n--- Generated CV Text ---")
        print(cv_text)
        print("--------------------------")
        with open('test_cv.pdf', 'wb') as f:
            f.write(pdf_bytes)
        print("PDF saved as test_cv.pdf")

    asyncio.run(main())
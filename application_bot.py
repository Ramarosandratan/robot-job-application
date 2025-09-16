import asyncio
import os
from playwright.async_api import Playwright, async_playwright, expect
from dotenv import load_dotenv

load_dotenv()

async def submit_application(job_data: dict, user_profile: dict, cover_letter_text: str) -> bool:
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            application_link = job_data.get("application_link")
            if not application_link:
                print("Error: No application link provided in job_data.")
                return False

            await page.goto(application_link)
            print(f"Navigated to: {application_link}")

            # Fill out common fields
            # Name
            if user_profile.get("name"):
                await page.fill("input[name*='name' i], input[id*='name' i]", user_profile["name"])
                print(f"Filled name: {user_profile['name']}")

            # Email
            if user_profile.get("email"):
                await page.fill("input[name*='email' i], input[id*='email' i]", user_profile["email"])
                print(f"Filled email: {user_profile['email']}")

            # Phone
            if user_profile.get("phone"):
                await page.fill("input[name*='phone' i], input[id*='phone' i]", user_profile["phone"])
                print(f"Filled phone: {user_profile['phone']}")

            # Upload CV
            cv_path = os.getenv("CV_PATH", "path/to/your/cv.pdf") # Placeholder for now
            if os.path.exists(cv_path):
                await page.set_input_files("input[type='file' i]", cv_path)
                print(f"Uploaded CV from: {cv_path}")
            else:
                print(f"Warning: CV file not found at {cv_path}. Skipping CV upload.")

            # Paste Cover Letter
            if cover_letter_text:
                await page.fill("textarea[name*='coverletter' i], textarea[id*='coverletter' i], textarea[name*='message' i], textarea[id*='message' i], textarea[aria-label*='cover letter' i]", cover_letter_text)
                print("Pasted cover letter text.")

            # Click submit button
            await page.click("button[type='submit' i], input[type='submit' i], button:has-text('Submit' i), button:has-text('Apply' i)")
            print("Clicked submit button.")

            # Basic success check (can be improved with more specific selectors or navigation checks)
            await page.wait_for_timeout(3000) # Wait for a few seconds to see if a success message appears
            if "success" in page.url.lower() or "thank you" in await page.content():
                print("Application appears to be submitted successfully.")
                return True
            else:
                print("Application submission status is uncertain. No clear success message or redirection.")
                return False

        except Exception as e:
            print(f"An error occurred during application submission: {e}")
            return False
        finally:
            await browser.close()

if __name__ == "__main__":
    # Example Usage (for testing purposes)
    async def main():
        dummy_job_data = {
            "application_link": "https://www.example.com/apply", # Replace with a real application link for testing
            "title": "Software Engineer",
            "company": "Example Corp"
        }
        dummy_user_profile = {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "123-456-7890"
        }
        dummy_cover_letter = "Dear Hiring Manager, I am very interested in this position..."

        print("Attempting to submit application...")
        success = await submit_application(dummy_job_data, dummy_user_profile, dummy_cover_letter)
        print(f"Application submission successful: {success}")

    asyncio.run(main())
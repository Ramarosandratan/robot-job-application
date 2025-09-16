import asyncio
from playwright.async_api import async_playwright, Page

async def get_job_title(url: str, page: Page | None = None) -> str | None:
    """
    Navigates to a given URL using Playwright and extracts the job title.
    Assumes the job title is within an <h1> tag or a <div> with class 'job-title'.
    If a page object is provided, it uses the existing page; otherwise, it launches a new browser and page.
    """
    browser = None
    if page is None:
        p = await async_playwright().start()
        browser = await p.chromium.launch()
        page = await browser.new_page()
    
    try:
        await page.goto(url)
        # Attempt to find job title in an h1 tag
        h1_title = await page.query_selector("h1")
        if h1_title:
            return await h1_title.text_content()

        # Attempt to find job title in a div with class 'job-title'
        div_title = await page.query_selector("div.job-title")
        if div_title:
            return await div_title.text_content()

        return None  # No job title found
    except Exception as e:
        print(f"Error scraping {url}: {e}")
        return None
    finally:
        if browser: # Only close browser if it was launched in this function
            await browser.close()
            await p.stop()

async def get_job_details(url: str, page: Page | None = None) -> dict | None:
    """
    Navigates to a given URL using Playwright and extracts the job description and relevant skills.
    Assumes the job description is within a <div> or <section> with class 'job-description' or 'description'.
    If a page object is provided, it uses the existing page; otherwise, it launches a new browser and page.
    """
    browser = None
    if page is None:
        p = await async_playwright().start()
        browser = await p.chromium.launch()
        page = await browser.new_page()
    
    job_details = {"description": None, "skills": []}
    try:
        await page.goto(url)

        # Extract job description
        description_element = await page.query_selector("div.job-description, section.job-description, div.description, section.description")
        if description_element:
            job_details["description"] = await description_element.text_content()

        # Extract skills from description
        if job_details["description"]:
            common_skills = ["Python", "SQL", "JavaScript", "AWS", "Docker", "Kubernetes", "React", "Angular", "Vue.js", "Node.js", "TypeScript", "Java", "C#", "Go", "Rust", "Azure", "GCP", "Terraform", "Ansible", "Git", "CI/CD", "Agile", "Scrum", "Linux", "Bash", "Data Science", "Machine Learning", "Deep Learning", "Pandas", "NumPy", "Scikit-learn", "TensorFlow", "PyTorch", "Spark", "Hadoop", "Kafka", "MongoDB", "PostgreSQL", "MySQL", "Redis", "GraphQL", "REST API", "Microservices", "Frontend", "Backend", "Fullstack", "DevOps", "Cloud", "Security", "Networking", "Blockchain", "AI", "NLP", "Computer Vision"]
            found_skills = [skill for skill in common_skills if skill.lower() in job_details["description"].lower()]
            job_details["skills"] = list(set(found_skills)) # Remove duplicates

        return job_details
    except Exception as e:
        print(f"Error scraping job details from {url}: {e}")
        return None
    finally:
        if browser: # Only close browser if it was launched in this function
            await browser.close()
            await p.stop()

import datetime

async def get_publication_date(url: str, page: Page | None = None) -> str | None:
    """
    Navigates to a given URL using Playwright and extracts the publication date.
    Assumes the date is typically found within a <span>, <div>, or <p> tag
    with a specific class or attribute (e.g., 'date-posted', 'posted-on', 'job-date').
    Attempts to parse the date into 'YYYY-MM-DD' format.
    If a page object is provided, it uses the existing page; otherwise, it launches a new browser and page.
    """
    browser = None
    if page is None:
        p = await async_playwright().start()
        browser = await p.chromium.launch()
        page = await browser.new_page()
    
    try:
        await page.goto(url)
        
        # Common selectors for publication date
        date_selectors = [
            "span.date-posted", "div.date-posted", "p.date-posted",
            "span.posted-on", "div.posted-on", "p.posted-on",
            "span.job-date", "div.job-date", "p.job-date",
            "[itemprop='datePosted']", # Schema.org common attribute
            "time" # HTML5 time element
        ]

        date_text = None
        for selector in date_selectors:
            date_element = await page.query_selector(selector)
            if date_element:
                date_text = await date_element.text_content()
                if date_text:
                    break
        
        if date_text:
            # Attempt to parse the date
            try:
                # Try common date formats
                parsed_date = None
                formats = [
                    "%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y",
                    "%Y/%m/%d", "%m/%d/%Y", "%d-%m-%Y"
                ]
                for fmt in formats:
                    try:
                        parsed_date = datetime.datetime.strptime(date_text.strip(), fmt)
                        break
                    except ValueError:
                        continue
                
                if parsed_date:
                    return parsed_date.strftime("%Y-%m-%d")
            except Exception as parse_e:
                print(f"Could not parse date '{date_text}': {parse_e}")
        
        return None # No date found or parsed
    except Exception as e:
        print(f"Error scraping publication date from {url}: {e}")
        return None
    finally:
        if browser: # Only close browser if it was launched in this function
            await browser.close()
            await p.stop()

async def get_company_and_location(url: str, page: Page | None = None) -> dict | None:
    """
    Navigates to a given URL using Playwright and extracts the company name and job location.
    Assumes company name is within a <span>, <div>, or <a> tag with common classes/attributes.
    Assumes location is within a <span>, <div>, or <p> tag with common classes/attributes.
    If a page object is provided, it uses the existing page; otherwise, it launches a new browser and page.
    """
    browser = None
    if page is None:
        p = await async_playwright().start()
        browser = await p.chromium.launch()
        page = await browser.new_page()
    
    company_info = {"company_name": None, "location": None}
    try:
        await page.goto(url)

        # Common selectors for company name
        company_selectors = [
            "span.company-name", "div.company-name", "a.company-name",
            "span.employer", "div.employer", "a.employer",
            "span.hiring-company", "div.hiring-company", "a.hiring-company",
            "[data-testid='company-name']", # Common attribute in some job boards
            "a[href*='company']" # Link to company profile
        ]

        for selector in company_selectors:
            company_element = await page.query_selector(selector)
            if company_element:
                company_info["company_name"] = await company_element.text_content()
                if company_info["company_name"]:
                    break
        
        # Common selectors for location
        location_selectors = [
            "span.job-location", "div.job-location", "p.job-location",
            "span.location", "div.location", "p.location",
            "span.address", "div.address", "p.address",
            "[data-testid='job-location']", # Common attribute in some job boards
        ]

        for selector in location_selectors:
            location_element = await page.query_selector(selector)
            if location_element:
                company_info["location"] = await location_element.text_content()
                if company_info["location"]:
                    break

        return company_info
    except Exception as e:
        print(f"Error scraping company and location from {url}: {e}")
        return None
    finally:
        if browser: # Only close browser if it was launched in this function
            await browser.close()
            await p.stop()


async def get_application_link(url: str, page: Page | None = None) -> str | None:
    """
    Navigates to a given URL using Playwright and extracts the direct application link.
    Looks for specific text in <a> tags or specific classes/IDs.
    If a direct link is not found, it tries to find a link leading to the company's application page.
    If a page object is provided, it uses the existing page; otherwise, it launches a new browser and page.
    """
    browser = None
    if page is None:
        p = await async_playwright().start()
        browser = await p.chromium.launch()
        page = await browser.new_page()
    
    try:
        await page.goto(url)

        # Common selectors and text for direct application links
        apply_selectors = [
            "a.apply-button", "a.application-link",
            "a:has-text('Apply Now')", "a:has-text('Postuler')", "a:has-text('Candidater')",
            "a[href*='apply']", "a[href*='application']"
        ]

        for selector in apply_selectors:
            link_element = await page.query_selector(selector)
            if link_element:
                href = await link_element.get_attribute("href")
                if href:
                    return href if href.startswith("http") else page.url + href
        
        # If no direct link, try to find a link to the company's application page
        company_apply_selectors = [
            "a[href*='careers']", "a[href*='jobs']", "a[href*='hiring']"
        ]

        for selector in company_apply_selectors:
            link_element = await page.query_selector(selector)
            if link_element:
                href = await link_element.get_attribute("href")
                if href:
                    return href if href.startswith("http") else page.url + href

        return None  # No application link found
    except Exception as e:
        print(f"Error scraping application link from {url}: {e}")
        return None
    finally:
        if browser: # Only close browser if it was launched in this function
            await browser.close()
            await p.stop()


async def scrape_jobs_from_search_page(search_url: str, max_pages: int = 5) -> list[dict]:
    """
    Navigates through multiple pages of job search results, extracts individual job URLs,
    and then scrapes details for each job.
    """
    all_job_data = []
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page: Page = await browser.new_page()
        try:
            await page.goto(search_url)
            print(f"Navigated to search URL: {search_url}")

            for i in range(max_pages):
                print(f"Scraping page {i + 1} of {max_pages}...")
                await page.wait_for_load_state("networkidle")

                # Extract individual job posting URLs
                # Common selectors for job links on a search results page
                job_link_selectors = [
                    "a.job-card-link", "a.job-listing-link", "a[data-testid='job-result']",
                    "div.job-result-card a", "li.job-item a"
                ]
                
                job_urls = []
                for selector in job_link_selectors:
                    elements = await page.query_selector_all(selector)
                    for element in elements:
                        href = await element.get_attribute("href")
                        if href:
                            # Ensure the URL is absolute
                            if not href.startswith("http"):
                                href = page.url.split('/')[0] + '//' + page.url.split('/')[2] + href
                            job_urls.append(href)
                    if job_urls: # If we found links with one selector, we can stop
                        break
                
                job_urls = list(set(job_urls)) # Remove duplicates
                print(f"Found {len(job_urls)} job URLs on page {i + 1}.")

                for job_url in job_urls:
                    print(f"Scraping details for: {job_url}")
                    job_data = {"url": job_url}
                    
                    # Pass the existing page object to avoid re-launching browser for each job
                    job_data["title"] = await get_job_title(job_url, page)
                    details = await get_job_details(job_url, page)
                    if details:
                        job_data.update(details)
                    job_data["publication_date"] = await get_publication_date(job_url, page)
                    company_location = await get_company_and_location(job_url, page)
                    if company_location:
                        job_data.update(company_location)
                    job_data["application_link"] = await get_application_link(job_url, page)
                    
                    all_job_data.append(job_data)
                
                # Locate and click the "next page" button
                next_page_selectors = [
                    "a.next-page", "button.pagination-next", "a[aria-label='Next']",
                    "a:has-text('Next')", "a:has-text('Suivant')"
                ]
                
                next_button = None
                for selector in next_page_selectors:
                    next_button = await page.query_selector(selector)
                    if next_button:
                        break
                
                if next_button and not await next_button.is_disabled():
                    print("Clicking next page button...")
                    await next_button.click()
                    await page.wait_for_load_state("networkidle")
                else:
                    print("Next page button not found or disabled. End of results.")
                    break # No more pages or button is disabled

        except Exception as e:
            print(f"Error during pagination scraping from {search_url}: {e}")
        finally:
            await browser.close()
    return all_job_data


if __name__ == "__main__":
    async def main():
        # Example usage for individual job scraping
        test_urls = [
            "https://www.example.com/job/software-engineer", # Example with h1
            "https://www.example.com/job/data-scientist",    # Example with div.job-title
            "https://www.example.com/job/no-title",          # Example with no title
            "https://www.example.com/job/fullstack-developer-with-python-and-react", # Example for job details
        ]

        print("--- Individual Job Scraping Examples ---")
        for url in test_urls:
            print(f"\nScraping individual job: {url}")
            title = await get_job_title(url)
            if title:
                print(f"Job Title: {title}")
            else:
                print(f"Job Title: Not found")

            details = await get_job_details(url)
            if details:
                print(f"Job Description: {details['description'][:200]}...")
                print(f"Skills: {', '.join(details['skills'])}")
            else:
                print(f"Job Details: Not found")
            
            publication_date = await get_publication_date(url)
            if publication_date:
                print(f"Publication Date: {publication_date}")
            else:
                print(f"Publication Date: Not found")

            company_info = await get_company_and_location(url)
            if company_info:
                print(f"Company: {company_info['company_name']}")
                print(f"Location: {company_info['location']}")
            else:
                print(f"Company and Location: Not found")

            application_link = await get_application_link(url)
            if application_link:
                print(f"Application Link: {application_link}")
            else:
                print(f"Application Link: Not found")

        # Example usage for search page scraping
        print("\n--- Search Page Scraping Example ---")
        search_page_url = "https://www.example.com/jobs?q=software+engineer" # Replace with a real search URL
        scraped_jobs = await scrape_jobs_from_search_page(search_page_url, max_pages=2)
        print(f"\nScraped {len(scraped_jobs)} jobs from search pages.")
        for i, job in enumerate(scraped_jobs):
            print(f"\nJob {i+1}:")
            for key, value in job.items():
                print(f"  {key}: {value}")

    asyncio.run(main())
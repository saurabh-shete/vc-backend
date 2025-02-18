from fastapi import APIRouter, HTTPException
from app.services.scraper import LinkedInScraper
from pydantic import BaseModel

router = APIRouter(prefix="/linkedin", tags=["LinkedIn Scraper"])


class ScrapeRequest(BaseModel):
    url: str
    session_cookie: str = (
        None  # Make sure to send a value, if not provided we attempt login
    )
    limit: int = 1


@router.post("/scrape_by_url")
async def scrape_profile_by_url(request: ScrapeRequest):
    url = request.url
    session_cookie = request.session_cookie
    limit = request.limit
    print(f"Limit: {limit}")

    # Initialize the scraper with the provided session cookie (if any)
    scraper = LinkedInScraper(session_cookie=session_cookie)
    if not session_cookie:
        login_success = scraper.login()
        if not login_success:
            scraper.close()  # Always close the driver
            raise HTTPException(status_code=400, detail="Login failed")

    profile = await scraper.scrape_profiles_by_url(url, limit)
    scraper.close()
    return {"profile": profile}

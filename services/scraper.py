import time
import os
import imaplib
import email
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from utils.linkedin_utils.extract_by_selectors_utils import extract_title_by_class
from utils.gemini_utils.agent import evaluate_profile_for_vc_json
from dotenv import load_dotenv

load_dotenv()

# Load credentials
LINKEDIN_EMAIL = os.getenv("LINKEDIN_EMAIL")
LINKEDIN_PASSWORD = os.getenv("LINKEDIN_PASSWORD")
IMAP_SERVER = os.getenv("IMAP_SERVER")
EMAIL_ACCOUNT = os.getenv("EMAIL_ACCOUNT")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")


class LinkedInScraper:

    def __init__(self, session_cookie: str = None):
        options = webdriver.ChromeOptions()
        options.add_argument("--headless")  # Run in headless mode (no UI)
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        service = Service("/usr/local/bin/chromedriver")
        self.driver = webdriver.Chrome(service=service, options=options)
        self.session_cookie = session_cookie
        if session_cookie:
            self._login_with_cookie()

    def _login_with_cookie(self):
        """
        Instead of logging in with username/password, use the provided li_at cookie.
        """
        # Navigate to LinkedIn to set the proper domain
        self.driver.get("https://www.linkedin.com")
        time.sleep(1)
        # Inject the li_at cookie
        self.driver.add_cookie(
            {
                "name": "li_at",
                "value": self.session_cookie,
                "domain": ".linkedin.com",
                "path": "/",
            }
        )
        # Refresh to apply the cookie
        self.driver.refresh()
        time.sleep(1)
        print("Logged in using session cookie")

    def login(self):
        """Logs into LinkedIn using Selenium."""
        if self.session_cookie:
            # Already logged in via cookie
            return True
        try:
            self.driver.get("https://www.linkedin.com/login")
            time.sleep(1)

            self.driver.find_element(By.ID, "username").send_keys(LINKEDIN_EMAIL)
            self.driver.find_element(By.ID, "password").send_keys(LINKEDIN_PASSWORD)
            self.driver.find_element(By.CSS_SELECTOR, "[type='submit']").click()
            time.sleep(1)

            # Check if email verification is required
            if "checkpoint/challenge" in self.driver.current_url:
                print("Verification required! Fetching code...")
                code = self.get_verification_code()
                if code:
                    self.driver.find_element(
                        By.ID, "input__email_verification_pin"
                    ).send_keys(code)
                    self.driver.find_element(By.ID, "email-pin-submit-button").click()
                    time.sleep(5)

            print("Login successful")
            return True
        except Exception as e:
            print(f"Error during login: {e}")
            return False

    def get_verification_code(self, retries=5, interval=4):
        """Fetch the latest verification code from Gmail."""
        try:
            mail = imaplib.IMAP4_SSL(IMAP_SERVER)
            mail.login(EMAIL_ACCOUNT, EMAIL_PASSWORD)
            mail.select("inbox")

            for attempt in range(retries):
                status, email_ids = mail.search(
                    None, '(FROM "security-noreply@linkedin.com")'
                )
                email_ids = email_ids[0].split()
                if not email_ids:
                    time.sleep(interval)
                    continue

                latest_email_id = email_ids[-1]
                status, email_data = mail.fetch(latest_email_id, "(RFC822)")
                raw_email = email_data[0][1]

                msg = email.message_from_bytes(raw_email)
                email_body = ""

                if msg.is_multipart():
                    for part in msg.walk():
                        if part.get_content_type() == "text/plain":
                            email_body = part.get_payload(decode=True).decode("utf-8")
                            break
                else:
                    email_body = msg.get_payload(decode=True).decode("utf-8")

                match = re.search(r"\b\d{6}\b", email_body)
                if match:
                    return match.group(0)

                time.sleep(interval)
            return None
        except Exception as e:
            print(f"Error fetching verification code: {e}")
            return None

    async def scrape_profiles_by_url(self, url, limit=1):
        """Scrape LinkedIn profiles based on industry & location."""
        search_url = url
        self.driver.get(search_url)
        time.sleep(1)

        # Wait for the search results to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, ".pv0.ph0.mb2.artdeco-card > ul[role='list']")
            )
        )
        # time.sleep(4)  # Allow extra time for profiles to render

        profile_links = []

        # Loop until we have enough profile links
        while len(profile_links) < limit:
            new_links = self.driver.execute_script(
                """
                 const profileLinks = [];
                    const ulSelector = '.pv0.ph0.mb2.artdeco-card > ul[role="list"]';
                    const ulElement = document.querySelector(ulSelector);
                    if (ulElement) {
                        const liElements = ulElement.children;
                        for (let i = 0; i < liElements.length; i++) {
                            const li = liElements[i];
                            const linkElement = li.querySelector('a');
                            if (linkElement) {
                                const href = linkElement.getAttribute('href');
                                if (href && href.includes('/in/')) {
                                    profileLinks.push(href);
                                }
                            }
                        }
                    }
                    return profileLinks;
                """
            )
            # print(new_links)
            # input("Press Enter to continue...")
            for link in new_links:
                if link not in profile_links:
                    profile_links.append(link)

            # Click "Next" if needed
            if len(profile_links) < limit:
                self.driver.execute_script(
                    "window.scrollTo(0, document.body.scrollHeight);"
                )
                self.driver.execute_script(
                    """
                        const nextButton = document.querySelector('button[aria-label="Next"]');
                        if (nextButton) {
                        if (!nextButton.disabled) {
                            nextButton.click();
                            console.log('Clicked the next button.');
                        } else {
                            console.log('The next button is disabled.');
                        }
                        } else {
                        console.error('Could not find the next button.');
                        }
                        """
                )
                time.sleep(1)

        # Only use the first 'limit' profile links
        profile_links = profile_links[:limit]
        print(f"Found {len(profile_links)} profile links!")

        # Extract details from each profile page
        profiles = []
        for profile_link in profile_links:
            self.driver.get(profile_link)
            time.sleep(1)
            linkedin_profile_link = profile_link.split("?")[0]
            try:
                # Wait for profile name and location
                top_panel = WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//*[@class='mt2 relative']")
                    )
                )

                name = top_panel.find_element(By.TAG_NAME, "h1").text
                title = extract_title_by_class(self.driver)
                location = top_panel.find_element(
                    By.XPATH,
                    "//*[@class='text-body-small inline t-black--light break-words']",
                ).text

                self.driver.get(f"{linkedin_profile_link}/details/experience/")
                time.sleep(1)

                experiences = self.driver.execute_script(
                    """
// Select only the top-level li elements
const mainUL = document.querySelector('.scaffold-finite-scroll__content > ul');
const liItems = mainUL.querySelectorAll(':scope > li:not([id*="profilePositionGroup"])');
const experiences = [];

liItems.forEach(item => {
  // Check if there are nested roles inside this item
  const nestedRole = item.querySelector('.pvs-entity__sub-components li[id*="profilePositionGroup"]');

  if (nestedRole) {
    // --- MULTI‑ROLE CONTAINER ---
    let company = '';
    const companyLink = item.querySelector('a[href*="linkedin.com/company"]');
    if (companyLink) {
      const img = companyLink.querySelector('img[alt]');
      if (img) {
        company = img.alt.replace(/logo/i, '').trim();
      }
    }
    
    // Process nested roles
    const nestedRoleItems = Array.from(
      item.querySelectorAll('.pvs-entity__sub-components li[id*="profilePositionGroup"]')
    );
    const roles = nestedRoleItems.map(nestedItem => {
      const titleEl = nestedItem.querySelector('.t-bold span[aria-hidden="true"]');
      const title = titleEl ? titleEl.innerText.trim() : '';

      let roleDateRange = '';
      let roleLocation = '';
      const detailContainer = nestedItem.querySelector('.display-flex.flex-column.full-width');
      if (detailContainer) {
        const spans = Array.from(detailContainer.querySelectorAll(':scope > span'));
        if (spans.length === 3) {
          const dateEl = spans[1].querySelector('span[aria-hidden="true"]');
          roleDateRange = dateEl ? dateEl.innerText.trim() : '';
          const locEl = spans[2].querySelector('span[aria-hidden="true"]');
          roleLocation = locEl ? locEl.innerText.trim() : '';
        } else if (spans.length === 2) {
          const dateEl = spans[0].querySelector('span[aria-hidden="true"]');
          roleDateRange = dateEl ? dateEl.innerText.trim() : '';
          const locEl = spans[1].querySelector('span[aria-hidden="true"]');
          roleLocation = locEl ? locEl.innerText.trim() : '';
        } else if (spans.length > 0) {
          const dateEl = spans[0].querySelector('span[aria-hidden="true"]');
          roleDateRange = dateEl ? dateEl.innerText.trim() : '';
        }
      }

      let roleDescription = [];
      nestedItem.querySelectorAll('.pvs-list__item--with-top-padding').forEach(bullet => {
        const bulletText = bullet.querySelector('span[aria-hidden="true"]')?.innerText.trim();
        if (bulletText && !bulletText.startsWith("Skills:")) {
          roleDescription.push(bulletText);
        }
      });
      
      return {
        title,
        dateRange: roleDateRange,
        location: roleLocation,
        description: roleDescription
      };
    });
    
    experiences.push({
      company,
      roles
    });
    
  } else {
    // --- SINGLE‑ROLE EXPERIENCE ---
    const titleEl = item.querySelector('.t-bold span[aria-hidden="true"]');
    if (!titleEl) return; // skip if no title found
    const title = titleEl.innerText.trim();
    
    let company = '';
    let dateRange = '';
    let location = '';
    const detailContainer = item.querySelector('.display-flex.flex-column.full-width');
    if (detailContainer) {
      const spans = Array.from(detailContainer.querySelectorAll(':scope > span'));
      if (spans.length === 3) {
        const compEl = spans[0].querySelector('span[aria-hidden="true"]');
        company = compEl ? compEl.innerText.trim() : '';
        const dateEl = spans[1].querySelector('span[aria-hidden="true"]');
        dateRange = dateEl ? dateEl.innerText.trim() : '';
        const locEl = spans[2].querySelector('span[aria-hidden="true"]');
        location = locEl ? locEl.innerText.trim() : '';
      } else if (spans.length === 2) {
        // When only two spans exist, try getting the company from the company link.
        const companyLink = item.querySelector('a[href*="linkedin.com/company"]');
        if (companyLink) {
          const img = companyLink.querySelector('img[alt]');
          if (img) {
            company = img.alt.replace(/logo/i, '').trim();
          }
        }
        const dateEl = spans[0].querySelector('span[aria-hidden="true"]');
        dateRange = dateEl ? dateEl.innerText.trim() : '';
        const locEl = spans[1].querySelector('span[aria-hidden="true"]');
        location = locEl ? locEl.innerText.trim() : '';
      }
    }
    
    let description = [];
    let skills = '';
    item.querySelectorAll('.pvs-entity__sub-components li.pvs-list__item--with-top-padding')
        .forEach(bullet => {
      const bulletText = bullet.querySelector('span[aria-hidden="true"]')?.innerText.trim();
      if (bulletText) {
        if (bulletText.startsWith("Skills:")) {
          skills = bulletText.replace("Skills:", "").trim();
        } else {
          description.push(bulletText);
        }
      }
    });
    
    experiences.push({
      title,
      company,
      dateRange,
      location,
      description,
      skills
    });
  }
});

return experiences;



"""
                )
                time.sleep(1)
                self.driver.get(f"{linkedin_profile_link}/details/education/")
                time.sleep(1)
                education = self.driver.execute_script(
                    """// Get the education container (assumed to be the div with class "scaffold-finite-scroll__content")
const eduContainer = document.querySelector('.scaffold-finite-scroll__content');

// Get the main UL containing all education LI items.
const eduUl = eduContainer ? eduContainer.querySelector('ul') : null;
const eduItems = eduUl ? Array.from(eduUl.children) : [];

// Array to hold the extracted education details.
const education = [];

eduItems.forEach(item => {
  // 1. Extract the institution name from the element with class "t-bold".
  //    (We pick the visible version by selecting the span with aria-hidden="true".)
  const institutionEl = item.querySelector('.t-bold span[aria-hidden="true"]');
  const institution = institutionEl ? institutionEl.innerText.trim() : '';

  // 2. Extract degree and date information.
  //    The details container is the element with classes
  //    "display-flex flex-column align-self-center flex-grow-1"
  let degree = '';
  let date = '';
  const detailsContainer = item.querySelector('.display-flex.flex-column.align-self-center.flex-grow-1');
  if (detailsContainer) {
    // Inside this container the education details are wrapped in an anchor.
    // (Note that in some entries there may be only one span containing the date.)
    const anchor = detailsContainer.querySelector('a.optional-action-target-wrapper.display-flex.flex-column.full-width');
    if (anchor) {
      // Select only the visible text for degree and date.
      const degreeEl = anchor.querySelector('span.t-14.t-normal:not(.t-black--light) span[aria-hidden="true"]');
      const dateEl = anchor.querySelector('span.t-14.t-normal.t-black--light span[aria-hidden="true"]');
      degree = degreeEl ? degreeEl.innerText.trim() : '';
      date = dateEl ? dateEl.innerText.trim() : '';
    }
  }
  
  // 3. Extract additional details (activities, coursework, etc.) from the nested sub-components.
  //    These details are in the UL inside the container with class "pvs-entity__sub-components".
  let details = [];
  const subComponents = item.querySelector('.pvs-entity__sub-components');
  if (subComponents) {
    const detailItems = subComponents.querySelectorAll('li');
    detailItems.forEach(li => {
      // Get the visible text inside each detail item.
      const textEl = li.querySelector('span[aria-hidden="true"]');
      if (textEl) {
        const text = textEl.innerText.trim();
        if (text) {
          details.push(text);
        }
      }
    });
  }
  
  // 4. Save the education entry.
  education.push({
    institution, // e.g. "Columbia University" or "Irvington High School"
    degree,      // e.g. "Bachelor of Arts - BA, Computer Science"
    date,        // e.g. "May 2024" or "2016 - 2020"
    details      // an array of additional details (activities, coursework, etc.)
  });
});

return education;
                                                       """
                )

                profile_data = {
                    "name": name,
                    "location": location,
                    "profile_url": linkedin_profile_link,
                    "title": title,
                    "experiences": experiences,
                    "education": education,
                }
                evaluation = await evaluate_profile_for_vc_json(profile_data)
                print(evaluation)
                profile_data["evaluation"] = evaluation

                profiles.append(profile_data)
                print(f"Scraped: {name} ({location})")

            except Exception as e:
                print(f"Error scraping {profile_link}: {e}")

        return profiles

    def close(self):
        self.driver.quit()

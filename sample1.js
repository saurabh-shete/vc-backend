// A helper function to extract details from one experience (or role) element
function extractRole(expElement) {
  const role = {};

  // Extract the job title – assume it's in an element with a bold class.
  const titleEl = expElement.querySelector(".t-bold span");
  role.title = titleEl ? titleEl.textContent.trim() : "";

  // Extract the company name and employment type.
  // For example, "Google · Full-time" might be in the first span with classes "t-14 t-normal"
  const companyEl = expElement.querySelector("span.t-14.t-normal");
  role.company = companyEl ? companyEl.textContent.trim() : "";

  // Extract the date range and location.
  // We expect two spans with the additional class "t-black--light": the first is the date, the second the location.
  const dateLocationEls = expElement.querySelectorAll(
    "span.t-14.t-normal.t-black--light"
  );
  role.date = dateLocationEls[0] ? dateLocationEls[0].textContent.trim() : "";
  role.location = dateLocationEls[1]
    ? dateLocationEls[1].textContent.trim()
    : "";

  // Extract the description using a more stable selector.
  // Instead of a fully dynamic class name, we match any element whose class attribute contains "inline-show-more-text".
  const descriptionEl = expElement.querySelector(
    "[class*='inline-show-more-text']"
  );
  role.description = descriptionEl ? descriptionEl.textContent.trim() : "";

  // Extract the company URL (from the anchor wrapping the company logo)
  const companyAnchor = expElement.querySelector(
    'a[href*="linkedin.com/company"]'
  );
  role.companyUrl = companyAnchor ? companyAnchor.href : "";

  // Extract the company logo URL from the image element (if available)
  const logoImg = expElement.querySelector('img[alt*="logo"]');
  role.logoUrl = logoImg ? logoImg.src : "";

  return role;
}

(function () {
  const profileCards = document.querySelectorAll(
    '[data-view-name="profile-card"]'
  );
  if (!profileCards.length) {
    console.error("No profile cards found.");
    return experiences;
  }

  profileCards.forEach((profileCard) => {
    const headerDiv = profileCard.querySelector("div");
    console.log(headerDiv);
    if (!headerDiv) return;
    const sectionName = headerDiv.id;

    // If the section is not Experience, move ahead.
    if (sectionName !== "experience") {
      const outerUl = Array.from(profileCard.querySelectorAll("ul")).find(
        (ul) => {
          return !ul.closest("li") && ul.querySelector("li");
        }
      );

      if (!outerUl) {
        console.error("Experience list not found");
        return;
      }

      // Select the top-level list items (direct children of the outer UL)
      const experienceItems = outerUl.querySelectorAll(":scope > li");
      const experiences = [];

      experienceItems.forEach((exp) => {
        // Extract details for the top-level experience
        const expData = extractRole(exp);

        // Check for a nested list of roles (for companies with multiple positions)
        const nestedList = exp.querySelector("ul");
        if (nestedList) {
          const nestedRoles = [];
          const nestedItems = nestedList.querySelectorAll("li");
          nestedItems.forEach((nestedExp) => {
            nestedRoles.push(extractRole(nestedExp));
          });
          expData.roles = nestedRoles;
        }

        experiences.push(expData);
      });

      // Output the extracted experiences to the console
      console.log(experiences);
    }
  });
})();

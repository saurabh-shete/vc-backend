function getExperiences() {
  const experiences = [];

  // Select all profile cards.
  const profileCards = document.querySelectorAll(
    '[data-view-name="profile-card"]'
  );
  if (!profileCards.length) {
    console.error("No profile cards found.");
    return experiences;
  }

  profileCards.forEach((profileCard) => {
    // In every section the first div tells which section it is.
    // (E.g., it may contain text like "Experience" or "Education".)
    const headerDiv = profileCard.querySelector("div");
    console.log(headerDiv);
    if (!headerDiv) return;
    const sectionName = headerDiv.id;

    // If the section is not Experience, move ahead.
    if (sectionName !== "experience") {
      // console.log(`Skipping section: ${sectionName}`);
      return;
    }
    console.log("Found section:", profileCard);
    // For the Experience section, look for the container with id="experience".
    // const experienceContainer = profileCard.querySelector("div#experience");
    // if (!experienceContainer) {
    //   console.warn("Experience container not found in this profile card.");
    //   return;
    // }
    // According to your requirement, the third div (index 2) in the experience container holds the main list.
    const mainList = profileCard.querySelectorAll(":scope > div")[2];

    if (!mainList) {
      console.error("No 3rd div found in the experience container.");
      return;
    }
    console.log(mainList);
    // In mainList, look for all <ul> elements – these represent the experience items.
    const oneDiv = mainList.querySelectorAll(":scope > ul")[0];
    //   console.log(onediv)
    const positions = Array.from(oneDiv.children).filter(
      (child) => child.tagName.toLowerCase() === "li"
    );

    console.log(positions);
    if (!positions.length) {
      console.warn("No experience items found in the container.");
      return;
    }
    // Process each experience item.
    // Find the container holding the details. It is marked by data-view-name="profile-component-entity".
    const profileEntity = positionItem.querySelector(
      "div[data-view-name='profile-component-entity']"
    );
    if (!profileEntity) return;
    // We expect two immediate children:
    // - The first for the company logo (to extract the LinkedIn URL)
    // - The second for the detailed information.
    const children = Array.from(profileEntity.children);
    if (children.length < 2) return;

    const companyLogoElem = children[0];
    const positionDetails = children[1];

    // --- Extract the company LinkedIn URL from the logo element ---
    const companyAnchor = companyLogoElem.querySelector("*");
    if (!companyAnchor) return;
    const companyLinkedinUrl = companyAnchor.getAttribute("href");
    if (!companyLinkedinUrl) return; // Skip if URL isn’t present

    // --- Get the position details ---
    const detailsChildren = Array.from(positionDetails.children);
    const positionSummaryDetails =
      detailsChildren.length > 0 ? detailsChildren[0] : null;
    const positionSummaryText =
      detailsChildren.length > 1 ? detailsChildren[1] : null;

    // Within the summary details, the first element (often a wrapper) contains a list of “outer positions.”
    let outerPositions = [];
    if (positionSummaryDetails && positionSummaryDetails.firstElementChild) {
      outerPositions = Array.from(
        positionSummaryDetails.firstElementChild.children
      );
    }

    // Initialize fields for the experience details.
    let positionTitle = "";
    let company = "";
    let workTimes = "";
    let location = "";

    // Depending on the number of items, choose a parsing strategy.
    if (outerPositions.length === 4) {
      // Assume order: [ title, company, work times, location ]
      positionTitle = outerPositions[0].querySelector("span")
        ? outerPositions[0].querySelector("span").textContent.trim()
        : "";
      company = outerPositions[1].querySelector("span")
        ? outerPositions[1].querySelector("span").textContent.trim()
        : "";
      workTimes = outerPositions[2].querySelector("span")
        ? outerPositions[2].querySelector("span").textContent.trim()
        : "";
      location = outerPositions[3].querySelector("span")
        ? outerPositions[3].querySelector("span").textContent.trim()
        : "";
    } else if (outerPositions.length === 3) {
      // Sometimes the third element contains a "·" character; use that to decide.
      if (outerPositions[2].textContent.includes("·")) {
        positionTitle = outerPositions[0].querySelector("span")
          ? outerPositions[0].querySelector("span").textContent.trim()
          : "";
        company = outerPositions[1].querySelector("span")
          ? outerPositions[1].querySelector("span").textContent.trim()
          : "";
        workTimes = outerPositions[2].querySelector("span")
          ? outerPositions[2].querySelector("span").textContent.trim()
          : "";
        location = "";
      } else {
        positionTitle = "";
        company = outerPositions[0].querySelector("span")
          ? outerPositions[0].querySelector("span").textContent.trim()
          : "";
        workTimes = outerPositions[1].querySelector("span")
          ? outerPositions[1].querySelector("span").textContent.trim()
          : "";
        location = outerPositions[2].querySelector("span")
          ? outerPositions[2].querySelector("span").textContent.trim()
          : "";
      }
    } else {
      // Fallback: assume at least one element gives the company name.
      positionTitle = "";
      company =
        outerPositions[0] && outerPositions[0].querySelector("span")
          ? outerPositions[0].querySelector("span").textContent.trim()
          : "";
      workTimes = "";
      location = "";
    }

    // --- Parse work times ---
    // Typically, the text is something like "Aug 2023 - Present · 1 yr 7 mos"
    let times = workTimes ? workTimes.split("·")[0].trim() : "";
    let duration =
      workTimes && workTimes.split("·").length > 1
        ? workTimes.split("·")[1].trim()
        : null;
    let fromDate = times ? times.split(" ").slice(0, 2).join(" ") : "";
    let toDate = times ? times.split(" ").slice(3).join(" ") : "";

    // --- Check for nested positions (multiple roles under the same company) ---
    let innerPositions = [];
    if (positionSummaryText) {
      // Look for an inner container with the class "pvs-list__container"
      const innerContainer = positionSummaryText.querySelector(
        ".pvs-list__container"
      );
      if (innerContainer) {
        innerPositions = Array.from(
          innerContainer.querySelectorAll(".pvs-list__paged-list-item")
        );
      }
    }

    if (innerPositions.length > 1) {
      // Process each nested role.
      innerPositions.forEach((innerItem) => {
        const anchor = innerItem.querySelector("a");
        if (!anchor) return;
        const res = Array.from(anchor.children);

        const posTitleElem = res.length > 0 ? res[0] : null;
        const workTimesElem = res.length > 1 ? res[1] : null;
        const locElem = res.length > 2 ? res[2] : null;

        const innerPositionTitle =
          posTitleElem && posTitleElem.querySelector("*")
            ? posTitleElem.querySelector("*").textContent.trim()
            : "";
        const innerWorkTimes =
          workTimesElem && workTimesElem.querySelector("*")
            ? workTimesElem.querySelector("*").textContent.trim()
            : "";
        const innerLocation =
          locElem && locElem.firstElementChild
            ? locElem.firstElementChild.textContent.trim()
            : null;

        const innerTimes = innerWorkTimes
          ? innerWorkTimes.split("·")[0].trim()
          : "";
        const innerDuration =
          innerWorkTimes && innerWorkTimes.split("·").length > 1
            ? innerWorkTimes.split("·")[1].trim()
            : null;
        const innerFromDate = innerTimes
          ? innerTimes.split(" ").slice(0, 2).join(" ")
          : "";
        const innerToDate = innerTimes
          ? innerTimes.split(" ").slice(3).join(" ")
          : "";

        experiences.push({
          section: sectionName,
          position_title: innerPositionTitle,
          from_date: innerFromDate,
          to_date: innerToDate,
          duration: innerDuration,
          location: innerLocation,
          description: innerItem.textContent.trim(),
          institution_name: company,
          linkedin_url: companyLinkedinUrl,
        });
      });
    } else {
      // No nested positions; use the top-level details.
      const description = positionSummaryText
        ? positionSummaryText.textContent.trim()
        : "";
      experiences.push({
        section: sectionName,
        position_title: positionTitle,
        from_date: fromDate,
        to_date: toDate,
        duration: duration,
        location: location,
        description: description,
        institution_name: company,
        linkedin_url: companyLinkedinUrl,
      });
    }
  });

  return experiences;
}

// For testing, run the function and log the results:
console.log(getExperiences());

// Kinu GEMINI API KEY
// For experiemnt use only
AIzaSyDNoyqSCcIavKveCZLdcaysWLsN19uKuYQ;

// Kinu GEMINI API KEY to be used in production
AIzaSyD7cadVNuT86ggQRif4bTKioy7tg4QJc30;

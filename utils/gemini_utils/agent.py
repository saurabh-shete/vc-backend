import os
import json
from google import genai
from google.genai import types
from starlette.concurrency import run_in_threadpool

# Create a client for the Gemini Developer API.
client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY"),
    http_options={"api_version": "v1alpha"},  # Adjust the API version if needed
)


async def evaluate_profile_for_vc_json(profile_data):
    """
    Constructs a prompt using the profile data and calls the Gemini API asynchronously.
    Ensures the response is in JSON format.
    """
    # Format the Education details
    education_str = "\n".join(
        f"- {edu.get('institution')}, {edu.get('degree')}, {edu.get('graduation_year', 'N/A')}. Details: {edu.get('details', '')}"
        for edu in profile_data.get("education", [])
    )

    # Format the Work Experience details
    experience_str = "\n".join(
        f"- {exp.get('role')} at {exp.get('company')} ({exp.get('duration')}, {exp.get('industry')}). Description: {exp.get('description')}"
        for exp in profile_data.get("experiences", [])
    )

    # Build the evaluation prompt with explicit instructions for JSON output.
    prompt = f"""
You are a profile evaluator for venture capital investment decisions. Evaluate the following LinkedIn profile and output your evaluation as a single valid JSON object with the following keys:

- "personal_information": an object with:
  - "score": a number between 0 and 100 evaluating the candidate's personal information (name, headline, location)
  - "explanation": a brief explanation of the score.
- "education": an object with:
  - "score": a number between 0 and 100 evaluating the candidate's education (degree, university, graduation year)
  - "explanation": a brief explanation of the score.
- "work_experience": an object with:
  - "score": a number between 0 and 100 evaluating the candidate's work experience (founder experience, startup involvement, tech/consulting background)
  - "explanation": a brief explanation of the score.
- "overall_score": a composite score between 0 and 100.
- "actionable_insights": an array of strings, each containing a key insight or actionable suggestion for VC decision-making.

**Important:** Your entire response must be a single JSON object with no additional text or formatting. Do not include any markdown formatting, comments, or extra text—only the JSON.

Profile Data:
Name: {profile_data.get("name")}
Headline: {profile_data.get("title")}
Location: {profile_data.get("location")}

Education:
{education_str}

Work Experience:
{experience_str}
    """

    # Call the Gemini model using the python-genai SDK asynchronously,
    # setting the expected MIME type to JSON.
    response = await run_in_threadpool(
        client.models.generate_content,
        model="gemini-2.0-flash-001",  # Replace with the appropriate model name if needed
        contents=prompt,
        config=types.GenerateContentConfig(
            max_output_tokens=600,  # Adjust token count if needed
            response_mime_type="application/json",
        ),
    )

    print(response)
    # Debug: If JSON parsing fails, print the raw output for inspection.
    try:
        evaluation_data = json.loads(response.text)
        return evaluation_data
    except json.JSONDecodeError:
        print("Error: Model returned invalid JSON")
        print("Raw output:", response.text)
        return {"error": "Invalid JSON response from AI model"}

from google import genai
from modules.config import GEMINI_API_KEY

client = genai.Client(
    api_key=GEMINI_API_KEY
)

def analyze_cv(cv_text):

    prompt = f"""
    Analyze this CV professionally.

    Include:
    - Professional summary
    - Key strengths
    - Technical skills
    - Weaknesses
    - Career recommendations

    CV:
    {cv_text}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text


def generate_interview_questions(cv_text):

    prompt = f"""
    Generate 5 professional interview questions
    based on this CV.

    Include:
    - Technical questions
    - Behavioral questions
    - Problem-solving questions

    CV:
    {cv_text}
    """

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )

    return response.text
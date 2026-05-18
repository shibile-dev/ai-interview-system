from google import genai
from modules.config import GEMINI_API_KEY

client = genai.Client(
    api_key=GEMINI_API_KEY
)

def evaluate_answer(question, answer):
    prompt = f"""
    You are an expert interview evaluator.
    
    Evaluate this interview answer professionally.
    
    Question: {question}
    Answer: {answer}
    
    Give scores out of 10 for:
    - Communication Score
    - Technical Score  
    - Confidence Score
    
    Then give:
    - Overall Score out of 10
    - 3 specific improvement suggestions
    
    Format your response EXACTLY like this:
    COMMUNICATION: X/10
    TECHNICAL: X/10
    CONFIDENCE: X/10
    OVERALL: X/10
    SUGGESTIONS:
    1. suggestion one
    2. suggestion two
    3. suggestion three
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    return response.text
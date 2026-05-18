from google import genai

client = genai.Client(
    api_key="AIzaSyDlMmHZCCuNls9WC71K6IJFsxixHBQ_jFg"
)

def detect_emotion(answer_text=""):
    if not answer_text:
        return "Neutral", 5, "No answer provided"
    
    prompt = f"""
    Analyze this interview answer and detect the candidate's emotional state.
    
    Answer: {answer_text}
    
    Respond EXACTLY in this format:
    EMOTION: [one of: Confident, Nervous, Focused, Calm, Excited, Uncertain]
    CONFIDENCE_SCORE: [number between 1-10]
    REASON: [one sentence explanation]
    """
    
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
    )
    
    text = response.text
    emotion = "Focused"
    confidence_score = 7
    reason = ""
    
    for line in text.split('\n'):
        if 'EMOTION:' in line:
            emotion = line.replace('EMOTION:', '').strip()
        if 'CONFIDENCE_SCORE:' in line:
            try:
                confidence_score = float(
                    line.replace('CONFIDENCE_SCORE:', '').strip()
                )
            except:
                confidence_score = 7
        if 'REASON:' in line:
            reason = line.replace('REASON:', '').strip()
    
    return emotion, confidence_score, reason
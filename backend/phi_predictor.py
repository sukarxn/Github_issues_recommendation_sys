from transformers import pipeline
import json

def create_phi_model():
    """Initialize a simpler model for text classification"""
    return pipeline("text-classification", 
                   model="distilbert-base-uncased",
                   return_all_scores=True)

def predict_experience_level(profile_text: str, model=None) -> str:
    """Predict experience level using sentiment analysis as a proxy"""
    if model is None:
        model = create_phi_model()
    
    # Use sentiment analysis scores as a proxy for experience level
    result = model(profile_text)
    sentiment_score = result[0][0]['score']  # Get the sentiment score
    
    # Map sentiment scores to experience levels
    if sentiment_score < 0.3:
        return 'beginner'
    elif sentiment_score < 0.7:
        return 'intermediate'
    else:
        return 'advanced'

def predict_programming_language(profile_text: str, model=None) -> str:
    """Extract programming language from text using keyword matching"""
    # List of common programming languages
    languages = ['python', 'javascript', 'java', 'c++', 'ruby', 'php', 'typescript', 'go', 'rust']
    
    # Convert to lowercase for case-insensitive matching
    text_lower = profile_text.lower()
    
    # Find all mentioned languages
    found_languages = [lang for lang in languages if lang in text_lower]
    
    # Return the first found language or 'python' as default
    return found_languages[0] if found_languages else 'python'

def analyze_profile(profile_text: str) -> dict:
    """Analyze a profile using Phi-4 to determine both experience level and language"""
    model = create_phi_model()  # Create model once to reuse
    
    experience_level = predict_experience_level(profile_text, model)
    language = predict_programming_language(profile_text, model)
    
    return {
        "experience_level": experience_level,
        "primary_language": language,
        "original_profile": profile_text
    }

if __name__ == "__main__":
    # Test with sample profile
    with open('sample_profile.txt', 'r') as f:
        sample_profile = f.read()
    
    results = analyze_profile(sample_profile)
    print(json.dumps(results, indent=2))
from openai import OpenAI
from dotenv import load_dotenv
import os

def test_openai_connection():
    print("Testing OpenAI API connection...")
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("Error: No API key found in .env file")
        return
    
    try:
        # Initialize client
        client = OpenAI(api_key=api_key)
        
        # Try a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5
        )
        
        print("Success! API connection working.")
        print(f"Response: {response.choices[0].message.content}")
        
    except Exception as e:
        print(f"Error connecting to OpenAI API: {str(e)}")
        print(f"Error type: {type(e)}")

if __name__ == "__main__":
    test_openai_connection() 
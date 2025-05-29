#!/usr/bin/env python3
"""
Test script to verify OpenAI API key is working correctly
"""
from config import OPENAI_API_KEY
from openai import OpenAI
import sys

def test_openai_api():
    """Test if the OpenAI API key is valid and working"""
    print("🔍 Testing OpenAI API Key...")
    print(f"API Key (partial): {OPENAI_API_KEY[:20]}...{OPENAI_API_KEY[-10:]}" if OPENAI_API_KEY else "❌ No API key found")
    
    if not OPENAI_API_KEY:
        print("❌ ERROR: No OpenAI API key found!")
        print("Please set your API key in config.json or .env file")
        return False
    
    try:
        # Initialize OpenAI client
        client = OpenAI(api_key=OPENAI_API_KEY)
        
        # Test with a simple completion
        print("🧪 Testing API connection...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Use standard model for testing
            messages=[
                {"role": "user", "content": "Say 'API test successful' if you can read this."}
            ],
            max_tokens=10
        )
        
        print("✅ SUCCESS: OpenAI API key is working!")
        print(f"Response: {response.choices[0].message.content}")
        return True
        
    except Exception as e:
        print(f"❌ ERROR: OpenAI API test failed!")
        print(f"Error details: {str(e)}")
        
        # Check for specific error types
        if "401" in str(e) or "invalid_api_key" in str(e):
            print("\n🔧 SOLUTION: Your API key appears to be invalid or expired")
            print("1. Go to https://platform.openai.com/api-keys")
            print("2. Create a new API key")
            print("3. Update your config.json file with the new key")
            print("4. Make sure you have credits in your OpenAI account")
        elif "429" in str(e):
            print("\n🔧 SOLUTION: Rate limit or quota exceeded")
            print("1. Check your OpenAI usage at https://platform.openai.com/usage")
            print("2. Add credits to your account if needed")
        else:
            print("\n🔧 SOLUTION: Check your internet connection and OpenAI service status")
        
        return False

if __name__ == "__main__":
    success = test_openai_api()
    if not success:
        sys.exit(1)
    print("\n🎉 Your OpenAI API setup is ready for the Kuku Coach API!") 
#!/usr/bin/env python3
"""
Test script to verify Google Gemini API setup
"""

import os
import sys
import time
from dotenv import load_dotenv

def main():
    print("🧪 Testing Google Gemini API Setup")
    print("===================================")
    
    # Load environment variables
    load_dotenv()
    
    # Check if API key is set
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY not found in environment variables")
        print("Please set this variable in your .env file")
        print("See docs/GEMINI_SETUP.md for instructions")
        return False
    
    if api_key in ["your-google-api-key-here", "YOUR_ACTUAL_GOOGLE_API_KEY_HERE"]:
        print("❌ GOOGLE_API_KEY is set to a placeholder value")
        print("Please replace it with your actual API key")
        print("See docs/GEMINI_SETUP.md for instructions")
        return False
    
    # Check if google-generativeai package is installed
    try:
        import google.generativeai as genai
        print("✅ google-generativeai package is installed")
    except ImportError:
        print("❌ google-generativeai package not found")
        print("Installing the package...")
        os.system("pip install -U google-generativeai")
        try:
            import google.generativeai as genai
            print("✅ google-generativeai package installed successfully")
        except ImportError:
            print("❌ Failed to install google-generativeai")
            print("Please install it manually: pip install -U google-generativeai")
            return False
    
    # Configure the API
    try:
        genai.configure(api_key=api_key)
        print("✅ Configured Google Generative AI with API key")
    except Exception as e:
        print(f"❌ Error configuring Google Generative AI: {e}")
        return False
    
    # Try to use a model
    model_names = [
        os.getenv("MODEL_QUESTIONS", "gemini-1.5-pro"),
        os.getenv("MODEL_TESTCASES", "gemini-1.5-flash"),
        "gemini-1.5-pro",  # Fallback if custom model names are invalid
    ]
    
    success = False
    for model_name in model_names:
        print(f"\n🔄 Testing model: {model_name}")
        try:
            # Try with newer API
            try:
                model = genai.GenerativeModel(model_name)
                response = model.generate_content("Hello, please respond with 'Gemini API is working!'")
                
                if hasattr(response, 'text'):
                    result = response.text
                else:
                    result = str(response)
                
                print(f"✅ Model {model_name} response: {result}")
                success = True
                break
                
            except AttributeError:
                # Try with older API pattern
                print("Using alternative API method...")
                model = genai.get_model(model_name)
                response = model.generate_text("Hello, please respond with 'Gemini API is working!'")
                print(f"✅ Model {model_name} response: {response}")
                success = True
                break
                
        except Exception as e:
            print(f"❌ Error with model {model_name}: {e}")
            print("Trying next model...")
            time.sleep(1)
    
    if success:
        print("\n✅ Google Gemini API setup is working correctly!")
        print("You're all set to generate questions and test cases.")
    else:
        print("\n❌ Unable to generate content with any model.")
        print("Please check your API key and ensure you have proper access.")
        print("See docs/GEMINI_SETUP.md for troubleshooting.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

# GEMINI CONFIGURATION GUIDE

This guide helps you set up and use Google's Gemini AI models with the TestCasesGenerator.

## Getting a Google Gemini API Key

1. Go to [Google AI Studio](https://ai.google.dev/)
2. Create a Google account or sign in with your existing account
3. Click on "Get API key" in the menu
4. Create a new API key
5. Copy the API key to your clipboard

## Configuration Steps

1. Open your `.env` file in the project root
2. Make sure `API_PROVIDER=gemini` is set
3. Add or update your Google API key:
   ```
   GOOGLE_API_KEY=your_api_key_here
   ```
4. Set your preferred models (or use the defaults):
   ```
   MODEL_QUESTIONS=gemini-1.5-pro
   MODEL_TESTCASES=gemini-1.5-flash
   ```

## Available Models

- `gemini-1.5-pro` - Best for complex reasoning and detailed output
- `gemini-1.5-flash` - Faster and more cost-effective for simpler tasks
- `gemini-1.0-pro` - Legacy model if needed

## Troubleshooting

If you encounter errors:

1. Verify your API key is correct and not a placeholder
2. Check if you have the latest version of the `google-generativeai` package
3. Ensure your Google account has billing set up if required
4. Check the API usage quotas in your Google AI Studio dashboard

## Package Installation

If you need to manually install or update the Google Generative AI package:

```bash
pip install -U google-generativeai
```

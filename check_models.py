# Import the required libraries
import os
from dotenv import load_dotenv
from google import genai

# Load the Gemini API key from the .env file
load_dotenv()

# Create the Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

# List models that support generating content
for model in client.models.list():
    if "generateContent" in (model.supported_actions or []):
        print(model.name)
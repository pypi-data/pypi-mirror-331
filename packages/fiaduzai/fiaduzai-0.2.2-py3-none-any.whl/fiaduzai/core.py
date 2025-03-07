import google.generativeai as genai
import textwrap
from IPython.display import Markdown, display

# Hardcoded API Key
API_KEY = "AIzaSyBm2V608qNDwMqnzgWjmrxvfkWc6bIgTm0"

# Configure the API key directly
genai.configure(api_key=API_KEY)

def to_markdown(text):
    """
    Convert plain text into a Markdown-formatted string.
    """
    text = text.replace('•', ' -')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

def generate_content(prompt):
    """
    Generate content using the Gemini model with the given prompt.
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content(prompt)
        answer = to_markdown(response.text)
        display(answer)
    except Exception as e:
        print(f"Error: {e}")

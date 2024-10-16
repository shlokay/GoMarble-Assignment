import os
import time
import json
from flask import Flask, jsonify, request, render_template
from bs4 import BeautifulSoup
import html2text
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from openai import AzureOpenAI, OpenAI 

app = Flask(__name__)

# Path to your msedgedriver
EDGE_DRIVER_PATH = './msedgedriver.exe'

# Azure OpenAI configuration
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME") or 'gpt-4o-mini'
API_VERSION = os.getenv("API_VERSION") or '2024-09-01-preview'
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 800))

#For Azure OpenAI:

# Initialize Azure OpenAI client
# client = AzureOpenAI(
#     azure_endpoint=AZURE_OPENAI_ENDPOINT,
#     api_key=AZURE_OPENAI_API_KEY,
#     api_version=API_VERSION,
# )

# For OpenAI:
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

def init_selenium():
    """Initialize and return Selenium WebDriver for Microsoft Edge."""
    options = Options()
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--inprivate")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    
    service = Service(EDGE_DRIVER_PATH)
    driver = webdriver.Edge(service=service, options=options)
    return driver

def retrieve_html(url):
    """Fetch HTML content from the URL using Selenium."""
    driver = init_selenium()
    try:
        driver.get(url)
        time.sleep(1)  # Simulate time for page load
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        page_source = driver.page_source
        return page_source
    finally:
        driver.quit()

def clean_html_content(raw_html):
    """Clean the HTML content by removing unnecessary tags like script, style, header."""
    soup = BeautifulSoup(raw_html, 'html.parser')
    for tag in soup(['header', 'footer', 'script', 'style']):
        tag.extract()
    return str(soup)

def convert_html_to_markdown(filtered_html):
    """Convert cleaned HTML to Markdown."""
    markdown_converter = html2text.HTML2Text()
    markdown_converter.ignore_links = False
    return markdown_converter.handle(filtered_html)

def split_content_for_processing(content, chunk_size=6000):
    """Split content into chunks for OpenAI processing."""
    return [content[i:i + chunk_size] for i in range(0, len(content), chunk_size)]

@app.route("/")
def home():
    """Render the home page."""
    return render_template("home.html")

@app.route("/api/reviews", methods=["GET"])
def show_results():
    """Fetch and display review information from a given URL."""
    try:
        url = request.args.get('page')
        if not url:
            return jsonify({"error": "URL parameter is missing"}), 400
        
        # Retrieve HTML content from the URL
        html_content = retrieve_html(url)
        markdown_content = convert_html_to_markdown(clean_html_content(html_content))
        content_chunks = split_content_for_processing(markdown_content)

        all_reviews = []

        for chunk in content_chunks:
            response = client.chat.completions.create(
                model=DEPLOYMENT_NAME,
                messages=[{"role": "system", "content": '''You are a helpful assistant that extracts review details from web content.
                    Format the reviews like this:
                    {
                        "reviews": [
                            {
                                "title": "Review Title",
                                "body": "Review content",
                                "rating": 5,
                                "reviewer": "Reviewer Name"
                            }
                        ]
                    }.'''},
                    {"role": "user", "content": chunk}
                ],
                max_tokens=MAX_TOKENS,
                temperature=0.0,
                top_p=0.95,
                stream=False
            )

            content = response.choices[0].message.content.strip()

            # Remove code block format if present
            if content.startswith("```json") and content.endswith("```"):
                content = content[7:-3].strip()

            try:
                reviews_data = json.loads(content)
                all_reviews.extend(reviews_data.get("reviews", []))
            except json.JSONDecodeError:
                print("Error parsing JSON:", content)

        # Prepare the response in the desired JSON format
        response_data = {
            "reviews_count": len(all_reviews),
            "reviews": all_reviews
        }

        return jsonify(response_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

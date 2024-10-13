import os
import time
from bs4 import BeautifulSoup
import html2text
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.edge.options import Options
from openai import AzureOpenAI

# Driver path for Edge WebDriver
EDGE_DRIVER_PATH = './msedgedriver.exe'

# Azure OpenAI credentials fetched from environment variables
AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
DEPLOYMENT_NAME = os.getenv("DEPLOYMENT_NAME")
API_VERSION = os.getenv("API_VERSION")
MAX_TOKENS = int(os.getenv("MAX_TOKENS", 800))

# Initialize Azure OpenAI client
client = AzureOpenAI(
    azure_endpoint=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY,
    api_version=API_VERSION,
)

# Function to configure and initialize the Selenium Edge WebDriver
def init_selenium():
    edge_options = Options()
    edge_options.add_argument("--disable-gpu")
    edge_options.add_argument("--disable-dev-shm-usage")
    edge_options.add_argument("--window-size=1920,1080")
    edge_options.add_argument("--inprivate")
    edge_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")

    edge_service = Service(executable_path=EDGE_DRIVER_PATH)
    driver = webdriver.Edge(service=edge_service, options=edge_options)
    return driver

# Function to retrieve the webpage's HTML content using Selenium
def get_page_html(url):
    driver = init_selenium()
    try:
        driver.get(url)
        time.sleep(1)  # Wait for the page to load fully
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Scroll down the page
        html_content = driver.page_source
        return html_content
    finally:
        driver.quit()

# Clean the HTML by removing unnecessary tags like scripts, styles, etc.
def remove_extra_html_tags(html):
    soup = BeautifulSoup(html, 'html.parser')
    for unwanted_tag in soup.find_all(['header', 'footer', 'script', 'style']):
        unwanted_tag.extract()
    return str(soup)

# Convert HTML content to markdown, ensuring readability
def convert_html_to_markdown(html):
    cleaned_html = remove_extra_html_tags(html)
    markdown_parser = html2text.HTML2Text()
    markdown_parser.ignore_links = False
    return markdown_parser.handle(cleaned_html)

# Split large DOM content into manageable chunks for processing
def break_up_dom(dom_content, chunk_size=6000):
    return [dom_content[i:i + chunk_size] for i in range(0, len(dom_content), chunk_size)]

# Example flow: Fetch and process the HTML content, convert it, and send parts for OpenAI processing
html_data = get_page_html('https://www.amazon.in/HP-Black-Original-Ink-Cartridge/product-reviews/B09JT29NYS/ref=cm_cr_dp_d_show_all_btm?ie=UTF8&reviewerType=all_reviews')
markdown_data = convert_html_to_markdown(html_data)
dom_chunks = break_up_dom(markdown_data)

# Send each chunk to OpenAI and retrieve structured review content
for chunk in dom_chunks:
    response = client.chat.completions.create(
        model=DEPLOYMENT_NAME,
        messages=[
            {"role": "system", "content": '''You are an assistant that extracts review information from a webpage. The information provided is in HTML format. Return the reviews in a JSON format like this:
            "reviews": [{
                "title": "Review Title",
                "body": "Review body text",
                "rating": 5,
                "reviewer": "Reviewer Name"
            },
            ].'''},
            {"role": "user", "content": chunk},
        ],
        max_tokens=MAX_TOKENS,
        temperature=0.0,
        top_p=0.95,
        stream=False
    )
    output = response.choices[0].message.content
    print(output)

# Web Scraping and Review Extraction API using Flask, Selenium, and Azure OpenAI

This project provides an API built using Flask that scrapes product reviews from a given URL, processes the HTML content with Selenium, and extracts structured review information using Azure OpenAI services. The API returns JSON responses containing review titles, body, ratings, and reviewer names.

## Solution Approach

### 1. Web Scraping with Selenium
   - Selenium is used to load and scrape HTML content from the webpage. The Edge WebDriver runs in headless mode, fetching the entire page, including dynamic content like reviews.
   - After loading, the script scrolls to the bottom to ensure all content is loaded before extracting the HTML.

### 2. HTML Cleaning and Parsing
   - Using BeautifulSoup, the raw HTML is cleaned by removing unnecessary tags such as `<script>`, `<style>`, `<header>`, and `<footer>`.
   - The cleaned HTML is then converted to Markdown format using `html2text` to improve readability and simplify processing for the AI.

### 3. Processing with Azure OpenAI
   - The cleaned HTML is split into smaller chunks if too large, and these chunks are sent to Azure OpenAI for review extraction.
   - Azure OpenAI processes the content and returns structured review data in JSON format, containing the review title, body, rating, and reviewer name.

### 4. API Endpoint
   - The API exposes the `/api/fetch-reviews` endpoint where users can input a URL to retrieve structured review data.

---

## System Architecture

Here is the high-level architecture illustrating the key components and interactions:

```plaintext
Client ----> Flask API ----> Selenium Web Scraping (Edge WebDriver)
      \                               |
       \-> Azure OpenAI Service <------|
```

## How to Run the Project

### Prerequisites
- Python 3.x installed
- Flask and required dependencies (`Flask`, `beautifulsoup4`, `html2text`, `selenium`)
- Microsoft Edge browser and Edge WebDriver installed
- An Azure OpenAI account with API key and access

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/shlokay/GoMarble-Assignment
    ```
2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   ```
3. Place the home.html in the templates folder
4. Place the styles.css in the static folder
5. Run the python file using the command:
   ```bash
   python main.py
   ```
### Screenshots:

Input page:
![input img](https://github.com/user-attachments/assets/e85b7f6f-27ed-455f-8200-531012354f78)
Result page:
![result op](https://github.com/user-attachments/assets/b645e307-e19e-4ed8-9090-cc2aabc186b2)
![res2 op](https://github.com/user-attachments/assets/0079e951-9f23-4188-92dd-9a6d737b20a6)


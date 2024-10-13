# Webpage Review Scraper with Azure OpenAI Integration

This project is a Python-based web scraper that extracts review information from product pages, processes the content using OpenAI's Azure API, and returns the reviews in structured JSON format. The project leverages Selenium for fetching the web content, BeautifulSoup for cleaning up the HTML, and Azure OpenAI for parsing and structuring the data.

## Features

- **Scraping Reviews:** Automatically scrape reviews from a given URL using Selenium Edge WebDriver.
- **HTML Parsing:** Clean up unnecessary HTML elements (like scripts, headers, and footers) using BeautifulSoup.
- **Conversion to Markdown:** Convert cleaned HTML content to Markdown format for readability.
- **Chunked Processing:** Break down large HTML content into manageable parts for efficient processing.
- **Azure OpenAI Integration:** Use Azure's OpenAI API to transform unstructured review content into a structured JSON format.

## Prerequisites

- **Python 3.7+**
- **Selenium WebDriver for Microsoft Edge**
- **Azure OpenAI Account**

### Libraries

- `selenium` - For automated browser control.
- `beautifulsoup4` - For HTML parsing and cleaning.
- `html2text` - For converting HTML to Markdown.
- `openai` - To interface with Azure OpenAI API.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/your-username/repo-name.git
cd repo-name

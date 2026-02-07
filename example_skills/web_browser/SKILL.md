# Web Browser Skill

## Description
This skill enables browsing and extracting information from any website. It provides tools to navigate web pages, search for content, and retrieve specific information from websites using web scraping techniques.

## Key Principles
- Always respect website terms of service and robots.txt
- Use reasonable delays between requests to avoid overloading servers
- Handle both static and dynamic content appropriately
- Focus on extracting publicly available information
- Use proper error handling for network issues and parsing failures

## Capabilities

### Web Navigation
- Visit and load web pages from any URL
- Handle HTTP redirects and status codes
- Support for custom headers and timeouts
- Basic authentication support if needed

### Content Extraction
- Extract page titles, meta descriptions, and headings
- Parse HTML content using CSS selectors
- Extract text content, links, and structured data
- Handle different content types (HTML, JSON, etc.)

### Search and Discovery
- Search for specific text within page content
- Extract elements by CSS selectors or XPath
- Find links, images, and other page elements
- Navigate through paginated content

## Usage

Execute Python scripts that use web scraping libraries to browse and extract information:

```python
import requests
from bs4 import BeautifulSoup

# Visit any website
url = "https://example.com"
response = requests.get(url)

if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    # Extract relevant information
    title = soup.find('title').text if soup.find('title') else "No title found"
    print(f"Page Title: {title}")
else:
    print(f"Failed to access {url}: {response.status_code}")
```

## Python Packages

This skill requires web scraping libraries:
- requests: For making HTTP requests
- beautifulsoup4: For HTML parsing and content extraction
- lxml: Optional XML/HTML parser (faster than standard library)

## Examples

### Example 1: Basic Page Information
**User Query:** What information can you find on a website?

**Response Plan:**
1. Visit the specified URL
2. Extract basic page information (title, description, headings)
3. Return formatted page summary

**Python Code:** See [examples/get_page_info.py](examples/get_page_info.py)

### Example 2: Content Search
**User Query:** Search for specific content on a website

**Response Plan:**
1. Load the webpage content
2. Search for specified keywords or patterns
3. Extract and return relevant sections

**Python Code:** See [examples/search_content.py](examples/search_content.py)

### Example 3: Extract Structured Data
**User Query:** Extract specific elements from a webpage

**Response Plan:**
1. Parse the HTML content
2. Use CSS selectors to find specific elements
3. Return structured data (lists, tables, etc.)

**Python Code:** See [examples/extract_elements.py](examples/extract_elements.py)

### Example 4: Link Discovery
**User Query:** Find all links on a webpage

**Response Plan:**
1. Parse the webpage
2. Extract all anchor tags and their href attributes
3. Return formatted list of links

**Python Code:** See [examples/find_links.py](examples/find_links.py)

## Notes

- Always respect website terms of service and robots.txt files
- Use reasonable delays between requests to avoid overloading servers
- Some websites may block automated requests - handle rate limiting gracefully
- JavaScript-heavy sites may require additional tools for full content access
- Consider using user agents that identify as automated tools when appropriate
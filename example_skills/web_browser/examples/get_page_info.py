import requests
from bs4 import BeautifulSoup

def get_page_info(url="https://example.com"):
    """Extract basic information from a webpage."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title
        title = soup.find('title')
        title_text = title.text.strip() if title else "No title found"

        # Look for description meta tag
        description = soup.find('meta', attrs={'name': 'description'})
        desc_text = description.get('content', '').strip() if description else ""

        # Look for main heading
        h1 = soup.find('h1')
        h1_text = h1.text.strip() if h1 else ""

        # Get all headings
        headings = []
        for level in ['h1', 'h2', 'h3']:
            for heading in soup.find_all(level):
                text = heading.get_text().strip()
                if text and len(text) < 100:
                    headings.append(f"{level.upper()}: {text}")

        result = f"""
Webpage Information:
URL: {url}
Title: {title_text}
Description: {desc_text}
Main Heading: {h1_text}

Headings Found:
"""
        for heading in headings[:10]:  # Limit to first 10 headings
            result += f"  {heading}\n"

        print(result.strip())

    except Exception as e:
        print(f"Error accessing webpage {url}: {e}")

# Example usage
if __name__ == "__main__":
    get_page_info("https://httpbin.org/html")
import requests
from bs4 import BeautifulSoup

def extract_elements(url="https://example.com", selector="p"):
    """Extract specific elements from a webpage using CSS selectors."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Try to find elements with the given selector
        elements = soup.select(selector)

        if elements:
            print(f"Found {len(elements)} elements matching selector '{selector}':")
            print()

            for i, elem in enumerate(elements[:20], 1):  # Limit to first 20 elements
                text = elem.get_text().strip()
                if text:
                    # Truncate long text
                    if len(text) > 200:
                        text = text[:200] + "..."

                    print(f"{i}. {text}")

                    # Show element attributes if interesting
                    attrs = elem.attrs
                    if attrs and len(str(attrs)) < 100:
                        print(f"   Attributes: {attrs}")

                    print()
        else:
            print(f"No elements found matching selector '{selector}'.")
            print("Try different selectors like: 'h1', 'p', '.class', '#id', 'div'")

            # Suggest some common elements that might exist
            suggestions = []
            if soup.find('h1'):
                suggestions.append("'h1' (main headings)")
            if soup.find('p'):
                suggestions.append("'p' (paragraphs)")
            if soup.find('div'):
                suggestions.append("'div' (content blocks)")
            if soup.find('a'):
                suggestions.append("'a' (links)")

            if suggestions:
                print(f"Suggested selectors to try: {', '.join(suggestions[:3])}")

    except Exception as e:
        print(f"Error extracting elements: {e}")

# Example usage
if __name__ == "__main__":
    extract_elements("https://httpbin.org/html", "h1")
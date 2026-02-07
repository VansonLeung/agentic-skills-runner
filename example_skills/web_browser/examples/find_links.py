import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def find_links(url="https://example.com"):
    """Find and extract all links from a webpage."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all anchor tags
        links = []
        for a_tag in soup.find_all('a', href=True):
            href = a_tag['href'].strip()
            text = a_tag.get_text().strip()

            # Convert relative URLs to absolute
            absolute_url = urljoin(url, href)

            # Clean up the link text
            if not text:
                text = "[No text]"
            elif len(text) > 50:
                text = text[:50] + "..."

            links.append({
                'url': absolute_url,
                'text': text,
                'is_external': urlparse(absolute_url).netloc != urlparse(url).netloc
            })

        if links:
            print(f"Found {len(links)} links on the webpage:")
            print()

            # Group by internal/external
            internal_links = [link for link in links if not link['is_external']]
            external_links = [link for link in links if link['is_external']]

            if internal_links:
                print("Internal Links:")
                for link in internal_links[:15]:  # Limit output
                    print(f"  {link['text']} -> {link['url']}")
                print()

            if external_links:
                print("External Links:")
                for link in external_links[:10]:  # Limit output
                    print(f"  {link['text']} -> {link['url']}")
                print()

            print(f"Total: {len(internal_links)} internal, {len(external_links)} external")
        else:
            print("No links found on the webpage.")

    except Exception as e:
        print(f"Error finding links: {e}")

# Example usage
if __name__ == "__main__":
    find_links("https://httpbin.org/html")
import requests
from bs4 import BeautifulSoup

def search_content(url="https://example.com", search_term="example"):
    """Search for specific content within a webpage."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')
        text_content = soup.get_text().lower()

        # Search for the term
        if search_term.lower() in text_content:
            print(f"Found '{search_term}' mentioned on the webpage.")

            # Extract surrounding context
            lines = soup.get_text().split('\n')
            relevant_lines = []

            for line in lines:
                if search_term.lower() in line.lower() and len(line.strip()) > 10:
                    # Clean up the line
                    clean_line = ' '.join(line.split())  # Normalize whitespace
                    if len(clean_line) < 200:  # Reasonable line length
                        relevant_lines.append(clean_line)

            if relevant_lines:
                print("Relevant content found:")
                for line in relevant_lines[:15]:  # Limit output
                    print(f"  {line}")
            else:
                print("Content found but context extraction limited.")
        else:
            print(f"'{search_term}' not found on the webpage.")
            print("Try different search terms or check the URL.")

    except Exception as e:
        print(f"Error searching webpage content: {e}")

# Example usage
if __name__ == "__main__":
    search_content("https://httpbin.org/html", "html")
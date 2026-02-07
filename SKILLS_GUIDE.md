# Creating Custom SKILLS

This guide explains how to create your own SKILLS for the LLM Skills Runner. SKILLS are modular capabilities that extend the LLM's functionality by allowing it to execute Python scripts for specific tasks.

## What is a SKILL?

A SKILL is a self-contained module that defines a specific capability, such as mathematical calculations, web browsing, file operations, or any other task that can be automated with Python code. Each SKILL consists of:

- **Documentation**: A `SKILL.md` file that describes the skill's purpose, usage, and examples
- **Dependencies**: An optional `requirements.txt` file listing Python packages needed
- **Examples**: An optional `examples/` folder with sample usage

## SKILL Folder Structure

```
SKILLS/
├── your_skill_name/
│   ├── SKILL.md          # Required: Skill documentation
│   ├── requirements.txt  # Optional: Python dependencies
│   ├── examples/         # Optional: Example files
│   └── venv/             # Auto-created: Virtual environment
```

## Creating a SKILL

### Step 1: Create the SKILL Folder

Create a new folder under `SKILLS/` with a descriptive name:

```bash
mkdir SKILLS/my_custom_skill
```

### Step 2: Write the SKILL.md File

The `SKILL.md` file is the core documentation that teaches the LLM how to use your skill. It should include:

#### Required Sections

- **# Skill Name**: A clear, descriptive title
- **## Description**: What the skill does and when to use it
- **## Key Principles**: Important guidelines for using the skill safely and effectively
- **## Examples**: Concrete examples showing how to use the skill

#### Example SKILL.md Structure

```markdown
# My Custom Skill

## Description
This skill allows you to [describe what it does]. It provides [key capabilities] by executing Python scripts that [explain the approach].

## Key Principles
- Always [important guideline]
- Handle [potential issues] appropriately
- Use [best practices] for [specific scenarios]

## Examples

### Example 1: Basic Usage
**User Query:** [Sample user request]

**Response Plan:**
1. [Step-by-step approach]
2. [Execution details]

**Python Code:**
```python
# Your Python script here
print("Hello, World!")
```

### Example 2: Advanced Usage
**User Query:** [More complex request]

**Response Plan:**
1. [Detailed steps]
2. [Error handling]

**Python Code:**
```python
# More complex script
import some_library
result = some_library.do_something()
print(result)
```
```

### Step 3: Add Dependencies (Optional)

If your skill requires external Python packages, create a `requirements.txt` file:

```
requests
beautifulsoup4
pandas
numpy
```

The system will automatically install these dependencies in a virtual environment when the skill is first used.

### Step 4: Add Examples (Optional)

Create an `examples/` folder with sample files, data, or additional documentation:

```
examples/
├── sample_input.txt
├── expected_output.json
├── usage_examples.md
```

## Best Practices

### Writing Effective SKILL.md Files

1. **Be Specific**: Clearly define what the skill can and cannot do
2. **Provide Examples**: Include multiple examples showing different use cases
3. **Include Error Handling**: Show how to handle common failure scenarios
4. **Use Clear Language**: Write in a way that an AI can understand and follow
5. **Document Limitations**: Explain any constraints or security considerations

### Code Quality

1. **Keep it Simple**: Use straightforward Python code that executes reliably
2. **Handle Errors**: Include try/catch blocks for network operations, file I/O, etc.
3. **Use Standard Libraries**: Prefer built-in modules when possible
4. **Output Clearly**: Use `print()` statements to output results the LLM can parse
5. **Respect Resources**: Avoid infinite loops, excessive memory usage, or long-running operations

### Security Considerations

1. **Validate Inputs**: Always validate and sanitize any user-provided data
2. **Limit Scope**: Only access resources that are explicitly needed
3. **Handle Sensitive Data**: Never log or expose passwords, API keys, or personal information
4. **Use Timeouts**: Implement reasonable timeouts for network operations
5. **Follow Ethics**: Respect terms of service, privacy laws, and ethical guidelines

## Testing Your SKILL

1. **Manual Testing**: Use the CLI to test your skill interactively:
   ```bash
   python -m skills_runner chat "Test your skill description"
   ```

2. **API Testing**: Test via the API endpoint:
   ```bash
   curl http://localhost:8000/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"model": "gpt-4", "messages": [{"role": "user", "content": "Test query"}]}'
   ```

3. **Verify Dependencies**: Ensure all required packages are listed in `requirements.txt`

## Real-World Examples

Here are complete examples from the actual SKILLS included in this project:

### Example 1: Calculator SKILL

The Calculator SKILL demonstrates a simple skill that performs mathematical operations.

#### SKILLS/calculator/SKILL.md
```markdown
# Calculator Skill

## Description
This skill lets you perform simple mathematical calculations, such as addition, subtraction, multiplication, and division. The LLM should write and execute Python code to compute results accurately.

## Key Principles
- Always use Python's built-in operators for calculations.
- Handle basic arithmetic operations.
- Output the result clearly, e.g., using `print()`.

## Examples

### Example 1: Addition
**User Query:** What is 5 + 7?

**Response Plan:**
1. Write a Python script to add the numbers.
2. Execute the script and return the result.

**Python Code:**
```python
print(5 + 7)
```

### Example 2: Subtraction
**User Query:** What is 10 - 3?

**Response Plan:**
1. Write a Python script to subtract the numbers.
2. Execute the script and return the result.

**Python Code:**
```python
print(10 - 3)
```

### Example 3: Multiplication
**User Query:** What is 6 * 4?

**Response Plan:**
1. Write a Python script to multiply the numbers.
2. Execute the script and return the result.

**Python Code:**
```python
print(6 * 4)
```

### Example 4: Division
**User Query:** What is 15 / 3?

**Response Plan:**
1. Write a Python script to divide the numbers.
2. Execute the script and return the result.

**Python Code:**
```python
print(15 / 3)
```

### Example 5: Complex Expression
**User Query:** What is (2 + 3) * 4 - 5?

**Response Plan:**
1. Write a Python script to evaluate the expression.
2. Execute the script and return the result.

**Python Code:**
```python
print((2 + 3) * 4 - 5)
```
```

#### SKILLS/calculator/requirements.txt
```
# No external dependencies needed for basic calculations
```

### Example 2: Web Browser SKILL

The Web Browser SKILL shows a more complex skill that requires external dependencies and handles web scraping.

#### SKILLS/web_browser/SKILL.md
```markdown
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
```

#### SKILLS/web_browser/requirements.txt
```
requests
beautifulsoup4
```

#### SKILLS/web_browser/examples/ Structure
```
examples/
├── get_page_info.py
├── search_content.py
├── extract_elements.py
└── find_links.py
```

## Contributing SKILLS

When creating SKILLS for the community:

1. **Follow Naming Conventions**: Use lowercase with underscores (e.g., `web_scraper`, `data_analyzer`)
2. **Document Thoroughly**: Provide comprehensive examples and edge cases
3. **Test Extensively**: Ensure your skill works reliably across different scenarios
4. **Consider Security**: Implement proper input validation and error handling
5. **Share Examples**: Include real-world usage examples in the `examples/` folder

## Getting Help

If you need help creating a SKILL:

1. Check existing SKILLS in the `SKILLS/` folder for reference
2. Test your SKILL using the CLI or API
3. Review the security considerations in the main README
4. Consider starting with a simple skill and gradually adding complexity

Remember: SKILLS run with the same permissions as the host system, so always prioritize security and reliability in your implementations.
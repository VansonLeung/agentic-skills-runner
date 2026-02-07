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

## Example: File Reader SKILL

Here's a complete example of a simple file reading skill:

### SKILLS/file_reader/SKILL.md
```markdown
# File Reader Skill

## Description
This skill allows you to read and analyze text files from the filesystem. It can extract content, search for patterns, and provide file information.

## Key Principles
- Only read files that are explicitly requested
- Handle file not found and permission errors gracefully
- Respect file encodings and use UTF-8 as default
- Limit output to reasonable sizes to avoid overwhelming responses

## Examples

### Example 1: Read Entire File
**User Query:** Read the contents of myfile.txt

**Response Plan:**
1. Check if file exists and is readable
2. Read the entire file content
3. Display the content with line numbers

**Python Code:**
```python
import os

filename = "myfile.txt"

if os.path.exists(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            print(f"{i:3}: {line}")
else:
    print(f"File '{filename}' not found.")
```

### Example 2: Search for Text
**User Query:** Find all lines containing "error" in log.txt

**Response Plan:**
1. Read the file line by line
2. Search for the specified text (case-insensitive)
3. Display matching lines with context

**Python Code:**
```python
import re

filename = "log.txt"
search_term = "error"

if os.path.exists(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for i, line in enumerate(lines, 1):
            if search_term.lower() in line.lower():
                print(f"Line {i}: {line.strip()}")
else:
    print(f"File '{filename}' not found.")
```
```

### SKILLS/file_reader/requirements.txt
```
# No external dependencies needed for basic file operations
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
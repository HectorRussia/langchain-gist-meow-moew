import requests
from bs4 import BeautifulSoup
from langchain.tools import Tool

def read_url_content(url: str) -> str:
    """Read content from a URL and return the text content."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text content
        text = soup.get_text()
        
        # Clean up the text
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        return text[:5000]  # Limit to first 5000 characters
        
    except Exception as e:
        return f"Error reading URL: {str(e)}"

# Create the tool
url_reader_tool = Tool(
    name="url_reader",
    description="Read content from a URL and return the text content. Input should be a valid URL.",
    func=read_url_content
)

# List of tools to export
tools = [url_reader_tool]
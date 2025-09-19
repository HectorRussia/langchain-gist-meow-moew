import requests
from bs4 import BeautifulSoup
import json

def clean_content(content: str) -> str:
    cleaned = ' '.join(content.split())
    return cleaned

def url_reader(url: str) -> str:

    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, "html.parser")

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        result = {
            "url": url,
            "title": soup.title.string.strip() if soup.title else "No title",
            "content": clean_content(soup.get_text().strip()[:5000]),  # Limit content length
            "status_code": response.status_code,
            "content_type": response.headers.get('content-type', ''),
        }
        return json.dumps(result, ensure_ascii=False, indent=2)
   
    except Exception as e:
        error_result = {
            "url": url,
            "error": f"Request failed: {str(e)}",
            "status": "failed"
        }
        return json.dumps(error_result, ensure_ascii=False, indent=2)


# Export the tool
# url_reader_tool = url_reader

result = url_reader("https://coinmarketcap.com/")

print(result)
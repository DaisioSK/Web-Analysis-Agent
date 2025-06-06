from fastapi import APIRouter
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests

router = APIRouter()

MCP_TOOL_META = {
    "name": "extract_images",
    "description": "extract all image links and their alt text from a webpage"
}

class URLInput(BaseModel):
    url: str

@router.post("/extract_images")
def extract_images(input: URLInput):
    try:
        url = input.url if input.url.startswith("http") else "https://" + input.url
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        images = []
        for img in soup.find_all("img"):
            src = img.get("src")
            alt = img.get("alt", "")
            if src:
                images.append({"src": src, "alt": alt})
        return {"images": images}
    except Exception as e:
        return {"error": str(e)}

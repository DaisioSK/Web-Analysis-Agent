from fastapi import APIRouter
from pydantic import BaseModel
from bs4 import BeautifulSoup
import requests
from langdetect import detect

router = APIRouter()

MCP_TOOL_META = {
    "name": "detect_language",
    "description": "detect the main language of the web page text."
}

class URLInput(BaseModel):
    url: str

@router.post("/detect_language")
def detect_language_tool(input: URLInput):
    try:
        url = input.url if input.url.startswith("http") else "https://" + input.url
        html = requests.get(url).text
        soup = BeautifulSoup(html, "html.parser")
        body_text = soup.get_text(separator=" ", strip=True)
        lang = detect(body_text)
        return {"language": lang}
    except Exception as e:
        return {"error": str(e)}

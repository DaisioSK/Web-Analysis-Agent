from playwright.sync_api import sync_playwright
from gradio_client import Client, handle_file
import cv2
import ast
import os
import json
import random
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, Tag
# import nest_asyncio


def capture_full_page_screenshot(url: str, output_path: str = "images/screenshot.png"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        if not url.startswith("http"):
            url = "https://" + url
        page.goto(url)

        page.wait_for_load_state("networkidle")

        page.set_viewport_size({
            "width": page.evaluate("() => document.body.scrollWidth"),
            "height": page.evaluate("() => document.body.scrollHeight")
        })

        page.screenshot(path=output_path, full_page=True)
        browser.close()

    print(f"Screenshot saved to {output_path}")

def clean_tag(tag: Tag) -> Tag:
    KEEP_ATTRIBUTES = ['aria-label', 'placeholder', 'alt', 'title', 'name', 'value']
    attrs = {}
    for k in tag.attrs:
        if k in KEEP_ATTRIBUTES:
            attrs[k] = tag.attrs[k]
    tag.attrs = attrs
    return tag

def deduplicate_components(components: list[dict]) -> list[dict]:
    """
    deduplicate based on tag + txt + attr
    """
    seen = set()
    deduped = []

    for comp in components:
        tag = comp.get("tag")
        txt = comp.get("txt", "").strip()
        attr = comp.get("attr", {})

        # use tuple(sorted(attr.items()))
        attr_tuple = tuple(sorted(attr.items()))
        key = (tag, txt, attr_tuple)

        if key not in seen:
            seen.add(key)
            deduped.append({"tag": tag, "txt": txt, "attr": dict(attr)})

    return deduped


def compress_components(components: list[dict]) -> list[dict]:
    """
    simplify compressed version: deduplicate all values of txt + attr for each tag, and join them with a space.
    oputput format: {tag: "value1 value2 value3"}
    """
    compressed = []

    for comp in components:
        tag = comp.get("tag")
        txt = comp.get("txt", "").strip()
        attr = comp.get("attr", {})

        parts = set()
        if txt:
            parts.add(txt.strip())

        for val in attr.values():
            if isinstance(val, str):
                clean = val.strip()
                if clean:
                    parts.add(clean)

        if parts:
            compressed.append({tag: " ".join(parts)})

    return compressed


async def extract_visible_dom_cleaned(url: str) -> list:
    
    if not url.startswith("http"):
        url = "https://" + url
            
    try: 
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle")

            get_visible_dom_script = """
            () => {
                const visibleTags = ['BUTTON', 'INPUT', 'A', 'IMG', 'TEXTAREA', 'SELECT', 'LABEL', 'FORM', 'DIV'];
                const isVisible = (elem) => {
                    const style = window.getComputedStyle(elem);
                    const rect = elem.getBoundingClientRect();
                    return (
                        style &&
                        style.display !== 'none' &&
                        style.visibility !== 'hidden' &&
                        style.opacity !== '0' &&
                        rect.width > 0 &&
                        rect.height > 0
                    );
                };
                const elements = Array.from(document.querySelectorAll(visibleTags.join(',')));
                return elements
                    .filter(isVisible)
                    .map(el => el.outerHTML);
            }
            """
            visible_elements = await page.evaluate(get_visible_dom_script)
            await browser.close()
            
        structured_components = []
        INTERACTIVE_TAGS = ['button', 'input', 'select', 'form', 'a']

        for outer_html in visible_elements:
            soup = BeautifulSoup(outer_html, 'html.parser')
            el = soup.find()

            if el and el.name in INTERACTIVE_TAGS:
                clean_tag(el) 
                txt = el.get_text(strip=True)
                attr = el.attrs
                if txt or attr:
                    structured_components.append({
                        "tag": el.name,
                        "txt": txt,
                        "attr": attr
                    })

        return structured_components

    except Exception as e:
        return f"[Extract DOM Error] {str(e)}"


async def parse_components_from_dom(url: str):
    print(">>> URL input type: ", type(url), url)
    raw = await extract_visible_dom_cleaned(url)
    deduped = deduplicate_components(raw)
    compressed = compress_components(deduped)
    return compressed


def parse_components_from_dom_sync(url: str):
    try:
        return asyncio.run(parse_components_from_dom(url))
    except Exception as e:
        return f"[Extract Clean DOM Error] {str(e)}"


def parse_ui_components_from_url(url):
    """
    parse a webpage UI screenshot, and provide a list of components with their coordinates
    """
    try:
        image_path = "images/screenshot.png"
        capture_full_page_screenshot(url, image_path)
        
        try:
            client = Client("microsoft/OmniParser-v2")
            result = client.predict(
                image_input=handle_file(image_path),
                box_threshold=0.05,
                iou_threshold=0.1,
                use_paddleocr=True,
                api_name="/process"
            )
        except Exception as e:
            print("OmniParser predict failed:", e)
            raise

        # print(result)
        (_, comp_lists) = result
        
        image = cv2.imread(image_path)
        height, width = image.shape[:2]
        
        components = []
        for line in comp_lists.strip().splitlines():
            try:
                icon_id = int(line.split(":", 1)[0].split()[1])
                comp = ast.literal_eval(line.split(":", 1)[1].strip())
                bbox = comp.get("bbox")
                label = comp.get("content", f"#{icon_id}")

                if isinstance(bbox, list) and len(bbox) == 4:
                    components.append({
                        "id": icon_id,
                        "bbox": bbox,
                        "label": label
                    })
            except Exception as e:
                print(f"Parse error on line: {line[:80]} → {e}")

        # visualize bbox
        last_color = None
        for comp in components:
            x1 = int(comp["bbox"][0] * width)
            y1 = int(comp["bbox"][1] * height)
            x2 = int(comp["bbox"][2] * width)
            y2 = int(comp["bbox"][3] * height)

            while True:
                color = tuple(random.randint(0, 255) for _ in range(3))
                if color != last_color:
                    break
            last_color = color

            cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
            cv2.putText(image, comp["label"], (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

        output_image_path = "images/output_annotated.png"
        cv2.imwrite(output_image_path, image)
        
        return {"components": components, 'analyzed_image': output_image_path}
        
    except Exception as e:
        return f"[OmniParser Error] {str(e)}"



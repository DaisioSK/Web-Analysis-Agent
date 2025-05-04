from playwright.sync_api import sync_playwright
from gradio_client import Client, handle_file
import json
import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup, Tag
# import nest_asyncio


def capture_full_page_screenshot(url: str, output_path: str = "images/screenshot.png"):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # 打开指定网页
        if not url.startswith("http"):
            url = "https://" + url
        page.goto(url)

        # 等待页面加载完成（可根据需要自定义更精细的等待策略）
        page.wait_for_load_state("networkidle")

        # 设置视窗为全屏（你也可以指定固定大小）
        page.set_viewport_size({
            "width": page.evaluate("() => document.body.scrollWidth"),
            "height": page.evaluate("() => document.body.scrollHeight")
        })

        # 截图整个页面
        page.screenshot(path=output_path, full_page=True)
        browser.close()

    print(f"Screenshot saved to {output_path}")

def clean_tag(tag: Tag) -> Tag:
    """只保留说明性属性"""
    KEEP_ATTRIBUTES = ['aria-label', 'placeholder', 'alt', 'title', 'name', 'value']
    attrs = {}
    for k in tag.attrs:
        if k in KEEP_ATTRIBUTES:
            attrs[k] = tag.attrs[k]
    tag.attrs = attrs
    return tag

def deduplicate_components(components: list[dict]) -> list[dict]:
    """
    基于 tag + txt + attr 结构去重
    """
    seen = set()
    deduped = []

    for comp in components:
        tag = comp.get("tag")
        txt = comp.get("txt", "").strip()
        attr = comp.get("attr", {})

        # 转成 hashable 的 key，attr 用 tuple 表示
        attr_tuple = tuple(sorted(attr.items()))
        key = (tag, txt, attr_tuple)

        if key not in seen:
            seen.add(key)
            deduped.append({"tag": tag, "txt": txt, "attr": dict(attr)})

    return deduped


def compress_components(components: list[dict]) -> list[dict]:
    """
    简化压缩版：把 tag 对应的 txt + attr 所有值去重后拼接，用空格连接。
    输出形式：{tag: "value1 value2 value3"}
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

            # 获取所有可见组件的 outerHTML
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
            
        # 结构化数据输出
        structured_components = []
        INTERACTIVE_TAGS = ['button', 'input', 'select', 'form', 'a']

        for outer_html in visible_elements:
            soup = BeautifulSoup(outer_html, 'html.parser')
            el = soup.find()

            if el and el.name in INTERACTIVE_TAGS:
                clean_tag(el)  # 清理属性
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
        output_path = "images/screenshot.png"
        capture_full_page_screenshot(url, output_path)
        client = Client("microsoft/OmniParser")
        result = client.predict(
            image_input=handle_file(output_path),
            box_threshold=0.05,
            iou_threshold=0.1,
            api_name="/process"
        )
        (_, cmp_desc, cmp_coord) = result
        return json.dumps({"components":cmp_desc, "coordinates":cmp_coord})
    except Exception as e:
        return f"[OmniParser Error] {str(e)}"



import os
import json
import requests
from pathlib import Path

# connection
FIGMA_FILE_KEY = "j4UeIYV6lCrtL6HGHRsOFY"   
FIGMA_TOKEN = "YOUR FIGMA_TOKEN "  
HEADERS = {"X-Figma-Token": FIGMA_TOKEN}
FIGMA_FILE_URL = f"https://api.figma.com/v1/files/{FIGMA_FILE_KEY}"
FIGMA_IMAGES_URL = f"https://api.figma.com/v1/images/{FIGMA_FILE_KEY}"

# Paths
IMAGE_LAYOUT_FILE = "perfect_layout_data.json"
OUTPUT_DIR = "angular-components"
Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

# function

def rgb_to_hex(color):
    """Convert Figma RGB object to HEX string."""
    if not color:
        return "#ffffff"
    r = int(color.get("r", 1) * 255)
    g = int(color.get("g", 1) * 255)
    b = int(color.get("b", 1) * 255)
    return f"#{r:02x}{g:02x}{b:02x}"

def fetch_figma_file():
    """Fetch full file JSON from Figma."""
    response = requests.get(FIGMA_FILE_URL, headers=HEADERS)
    response.raise_for_status()
    return response.json()

def get_canvas_background_color(figma_data):
    """Extract Canvas background color."""
    document = figma_data["document"]
    canvases = [node for node in document.get("children", []) if node["type"] == "CANVAS"]

    if not canvases:
        print("❌ No Canvas found.")
        return "#ffffff"

    canvas = canvases[0]
    bg_color_obj = canvas.get("backgroundColor")
    return rgb_to_hex(bg_color_obj)

def extract_main_frames(figma_data):
    """Extract frames inside Canvas."""
    frames = []
    document = figma_data["document"]
    canvases = [node for node in document.get("children", []) if node["type"] == "CANVAS"]

    if not canvases:
        print("❌ No Canvas found.")
        return frames

    canvas = canvases[0]

    def is_frame(node):
        return node.get("type") == "FRAME" and node.get("visible", True)

    for node in canvas.get("children", []):
        if is_frame(node):
            bbox = node.get("absoluteBoundingBox", {})
            frame_bg = node.get("backgroundColor")
            frames.append({
                "id": node["id"],
                "name": node.get("name", "Unnamed Frame"),
                "width": round(bbox.get("width", 0)),
                "height": round(bbox.get("height", 0)),
                "x": round(bbox.get("x", 0)),
                "y": round(bbox.get("y", 0)),
                "background_color": rgb_to_hex(frame_bg)
            })

    return frames

def fetch_exact_images(frame_ids):
    """Fetch frame images using Export API exactly matching frame size."""
    if not frame_ids:
        return {}

    ids_param = ",".join(frame_ids)
    try:
        export_url = f"{FIGMA_IMAGES_URL}?ids={ids_param}&format=png&use_absolute_bounds=true"
        res = requests.get(export_url, headers=HEADERS)
        res.raise_for_status()
        return res.json().get("images", {})
    except Exception as e:
        print(f"❌ Failed to fetch images: {e}")
        return {}

def merge_frames_with_images(frames, images):
    """Attach image URLs to frames."""
    for frame in frames:
        image_url = images.get(frame["id"])
        frame["image_url"] = image_url or "❌ Not Found"
    return frames

def load_image_layout():
    with open(IMAGE_LAYOUT_FILE, "r", encoding="utf-8") as f:
        layout_data = json.load(f)

    page_bg_color = layout_data.get("page_background_color", "#ffffff")

    for frame in layout_data.get("frames", []):
        if "background_color" not in frame:
            frame["background_color"] = "#ffffff"

    return layout_data, page_bg_color

def adjust_positions(frames):
    min_x = min(frame["x"] for frame in frames)
    min_y = min(frame["y"] for frame in frames)
    shift_x = -min_x if min_x < 0 else 0
    shift_y = -min_y if min_y < 0 else 0

    for frame in frames:
        frame["x"] += shift_x
        frame["y"] += shift_y
    return frames

def generate_html(image_layout, page_bg_color):
    html = [f'<div class="layout-wrapper" style="background-color: {page_bg_color};">']
    for frame in image_layout:
        frame_id = str(frame.get("id", "no-id")).replace(":", "-")
        width = f'{frame.get("width", 100)}px'
        height = f'{frame.get("height", 100)}px'
        x = f'{frame.get("x", 0)}px'
        y = f'{frame.get("y", 0)}px'
        name = frame.get("name", "Image")
        image_url = frame.get("image_url", "")
        background_color = frame.get("background_color", "#ffffff")

        html.append(f'''  <div class="frame frame-{frame_id}" style="width: {width}; height: {height}; left: {x}; top: {y}; background-color: {background_color};">''')

        if image_url:
            html.append(f'''    <img src="{image_url}" alt="{name}" style="width: 100%; height: 100%; object-fit: cover;" />''')
        else:
            html.append(f'''    <!-- No image available for {name} -->''')

        html.append('  </div>')
    html.append('</div>')
    return "\n".join(html)

def generate_css(image_layout):
    css = [
        "body { margin: 0; padding: 0; background: #f9f9f9; }",
        ".layout-wrapper {",
        "  position: relative;",
        "  width: 100%;",
        "  height: 100vh;",
        "  overflow: auto;",
        "}",
        "img {",
        "  display: block;",
        "}"
    ]
    for frame in image_layout:
        frame_id = str(frame.get("id", "no-id")).replace(":", "-")
        bg = frame.get("background_color", "#ffffff")
        css.append(f""".frame-{frame_id} {{
  position: absolute;
  background-color: {bg};
  flex-shrink: 0;
}}""")
    return "\n".join(css)

def generate_ts():
    return '''import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css']
})
export class AppComponent {
  title = 'FigmaToAngularLayout';
}
'''

def save_files(html, css, ts):
    with open(os.path.join(OUTPUT_DIR, "app.component.html"), "w", encoding="utf-8") as f:
        f.write(html)
    with open(os.path.join(OUTPUT_DIR, "app.component.css"), "w", encoding="utf-8") as f:
        f.write(css)
    with open(os.path.join(OUTPUT_DIR, "app.component.ts"), "w", encoding="utf-8") as f:
        f.write(ts)

# main
if __name__ == "__main__":
    try:
        # Fetch Figma file
        figma_data = fetch_figma_file()

        # Get Canvas background color
        canvas_background_color = get_canvas_background_color(figma_data)
        print(f"🎨 Canvas Background Color: {canvas_background_color}")

        # Extract frames
        frames = extract_main_frames(figma_data)
        print(f"✅ Found {len(frames)} frames.")

        # Fetch images
        frame_ids = [frame["id"] for frame in frames]
        images = fetch_exact_images(frame_ids)
        frames_with_images = merge_frames_with_images(frames, images)

        # Create final layout data
        layout_data = {
            "page_background_color": canvas_background_color,
            "frames": frames_with_images
        }

        # Save to JSON
        with open(IMAGE_LAYOUT_FILE, "w") as f:
            json.dump(layout_data, f, indent=2)

        print("✅ Perfect layout data saved to 'perfect_layout_data.json'.")

        # 7. Load layout data and generate Angular files
        layout_data, page_bg_color = load_image_layout()
        adjusted_data = adjust_positions(layout_data.get("frames", []))
        html_code = generate_html(adjusted_data, page_bg_color)
        css_code = generate_css(adjusted_data)
        ts_code = generate_ts()
        save_files(html_code, css_code, ts_code)

        print("✅ Webpage replicated with perfect image size, position, background color!")
        print("📁 Files saved to:", OUTPUT_DIR)

    except Exception as e:
        print(f"❌ Error: {e}")

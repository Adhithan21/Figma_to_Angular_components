import json
import os

def figma_to_angular(figma_json_path, output_dir):
    """Converts Figma JSON into an Angular component."""
    try:
        with open(figma_json_path, 'r', encoding='utf-8') as f:
            figma_data = json.load(f)

        frame = figma_data['document']['children'][0]['children'][0]
        component_name = frame['name'].replace(" ", "-").lower()
        class_name = ''.join(x.capitalize() for x in component_name.split('-')) + "Component"

        os.makedirs(output_dir, exist_ok=True)
        write_file(output_dir, f'{component_name}.component.html', generate_html(frame))
        write_file(output_dir, f'{component_name}.component.css', generate_css(frame))
        write_file(output_dir, f'{component_name}.component.ts', generate_ts(component_name, class_name))

        print(f"✅ Component '{component_name}' generated in '{output_dir}'.")
    except Exception as e:
        print(f"❌ Error: {e}")


def write_file(directory, filename, content):
    with open(os.path.join(directory, filename), 'w', encoding='utf-8') as f:
        f.write(content)


def extract_color(fills):
    """Extracts RGB color from Figma fills."""
    if fills and isinstance(fills, list) and "color" in fills[0]:
        r, g, b = (int(fills[0]["color"][c] * 255) for c in "rgb")
        return f"rgb({r}, {g}, {b})"
    return "transparent"


def generate_html(frame):
    """Generates HTML content based on Figma layers."""
    html = ""
    for child in frame.get('children', []):
        bbox = child.get('absoluteBoundingBox', {'x': 0, 'y': 0, 'width': 100, 'height': 100})
        styles = f"position: absolute; left: {bbox['x']}px; top: {bbox['y']}px; width: {bbox['width']}px; height: {bbox['height']}px;"
        
        if child['type'] == 'TEXT':
            styles += f" font-size: {child.get('style', {}).get('fontSize', 16)}px; color: {extract_color(child.get('fills', []))};"
            html += f'<p style="{styles}">{child.get("characters", "")}</p>\n'
        elif child['type'] == 'RECTANGLE':
            styles += f" background-color: {extract_color(child.get('fills', []))};"
            html += f'<div style="{styles}"></div>\n'
        elif child['type'] == 'ELLIPSE':
            styles += f" background-color: {extract_color(child.get('fills', []) )}; border-radius: 50%;"
            html += f'<div style="{styles}"></div>\n'
    return html


def generate_css(frame):
    """Generates CSS styles based on Figma layers."""
    css = ""
    for child in frame.get('children', []):
        if 'absoluteBoundingBox' in child:
            css += f".{child['name'].replace(' ', '-').lower()} {{\n"
            css += f"    position: absolute;\n"
            bbox = child['absoluteBoundingBox']
            css += f"    left: {bbox['x']}px; top: {bbox['y']}px;\n"
            css += f"    width: {bbox['width']}px; height: {bbox['height']}px;\n"
            if 'fills' in child:
                css += f"    background-color: {extract_color(child['fills'])};\n"
            css += "}\n\n"
    return css


def generate_ts(component_name, class_name):
    """Generates TypeScript for the Angular component."""
    return f"""
import {{ Component, OnInit }} from '@angular/core';

@Component({{
  selector: 'app-{component_name}',
  templateUrl: './{component_name}.component.html',
  styleUrls: ['./{component_name}.component.css']
}})
export class {class_name} implements OnInit {{
  constructor() {{ }}
  ngOnInit(): void {{ }}
}}
"""

figma_to_angular('figma.json', 'output_components')

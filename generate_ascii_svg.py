import sys
import subprocess
import html

try:
    from PIL import Image
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

def generate_animated_svg(image_path, output_path, new_width=60):
    try:
        img = Image.open(image_path).convert('L')
    except Exception as e:
        print(f"Error opening image: {e}")
        return

    # Resize image
    width, height = img.size
    aspect_ratio = height / width
    # Fonts are typically ~2 times as tall as they are wide, so we scale height by 0.5
    new_height = int(aspect_ratio * new_width * 0.5)
    img = img.resize((new_width, new_height))

    # Characters mapping from darkest to lightest
    # The image is black background with white lines, so black=space, white=character
    chars = [" ", ".", ":", "-", "=", "+", "*", "#", "%", "@"]
    
    pixels = img.getdata()
    ascii_str = ""
    for pixel_value in pixels:
        ascii_str += chars[pixel_value * (len(chars) - 1) // 255]
    
    # Split into lines
    ascii_str_len = len(ascii_str)
    ascii_img = [ascii_str[index: index + new_width] for index in range(0, ascii_str_len, new_width)]

    # Generate SVG
    font_size = 13
    line_height = 15
    char_width = font_size * 0.6  # Approximate width of monospace character
    svg_width = int(new_width * char_width) + 40
    svg_height = int(new_height * line_height) + 40
    duration_per_line = 0.09

    svg_content = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{svg_width}" height="{svg_height}" viewBox="0 0 {svg_width} {svg_height}" font-family="monospace">',
        '<style>.a{fill:#c9d1d9}</style>'
    ]

    for i, line in enumerate(ascii_img):
        start_time = i * duration_per_line
        y_clip = 14 + (i * line_height)
        y_text = 14 + (i * line_height) + 11.2  # offset for baseline
        y_rect = 15 + (i * line_height)
        
        # Calculate actual width of the line (removing trailing spaces for faster typing effect if we want, 
        # but for consistent width we can just use the full line or the stripped line)
        stripped_line = line.rstrip()
        if not stripped_line:
            continue
            
        line_char_count = len(stripped_line)
        line_width = line_char_count * char_width
        
        # Escape XML characters in text
        escaped_line = html.escape(stripped_line)

        svg_content.extend([
            f'<clipPath id="c{i}">',
            f'  <rect x="14" y="{y_clip}" height="{line_height}" width="0">',
            f'    <animate attributeName="width" from="0" to="{line_width}" begin="{start_time:.2f}s" dur="{duration_per_line}s" fill="freeze"/>',
            f'  </rect>',
            f'</clipPath>',
            f'<g clip-path="url(#c{i})">',
            f'  <text xml:space="preserve" x="14" y="{y_text}" class="a" font-size="{font_size}">{escaped_line}</text>',
            f'</g>',
            f'<rect y="{y_rect}" width="6" height="12" class="a" opacity="0">',
            f'  <animate attributeName="x" from="14" to="{line_width + 14}" begin="{start_time:.2f}s" dur="{duration_per_line}s" fill="freeze"/>',
            f'  <set attributeName="opacity" to="0.8" begin="{start_time:.2f}s"/>',
            f'  <set attributeName="opacity" to="0" begin="{start_time + duration_per_line:.2f}s"/>',
            f'</rect>'
        ])

    svg_content.append('</svg>')

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(svg_content))

    print(f"Successfully generated {output_path}")

if __name__ == "__main__":
    image_path = r"C:\Users\iceef\Downloads\IMG_6801.jpg"
    output_path = "animated-face.svg"
    # We use a relatively high width to capture the detail of the face
    generate_animated_svg(image_path, output_path, new_width=70)

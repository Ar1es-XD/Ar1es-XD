import os
import sys
import cv2
import numpy as np

def main():
    prepped_path = "source-prepped.png"
    output_path = "avi-ascii.svg"

    if not os.path.exists(prepped_path):
        print(f"Error: {prepped_path} does not exist. Run prep_photo.py first.")
        sys.exit(1)

    # Load prepped grayscale image
    img = cv2.imread(prepped_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Error: Could not read image {prepped_path}")
        sys.exit(1)

    # Grid config to fit exactly 370x490 card
    cols = 70
    rows = 50
    char_w = 4.8
    char_h = 8.5
    
    # Target physical aspect ratio of the character grid content
    target_aspect = (cols * char_w) / (rows * char_h)  # 336 / 425 = 0.790588

    # Crop image to match target aspect ratio around center to avoid distortion
    img_h, img_w = img.shape
    current_aspect = img_w / img_h
    if current_aspect > target_aspect:
        # Image is too wide, crop width
        new_w = int(img_h * target_aspect)
        start_x = (img_w - new_w) // 2
        img = img[:, start_x:start_x+new_w]
    else:
        # Image is too tall, crop height
        new_h = int(img_w / target_aspect)
        start_y = (img_h - new_h) // 2
        img = img[start_y:start_y+new_h, :]

    print(f"Cropped image to size {img.shape[1]}x{img.shape[0]} to match target aspect {target_aspect:.4f}")
    resized = cv2.resize(img, (cols, rows), interpolation=cv2.INTER_AREA)

    # ASCII character ramp (from brightest/space to darkest/dense)
    # White background (255) maps to spaces
    RAMP = " .`:-=+*cs#%@"

    lines = []
    for r in range(rows):
        line_chars = []
        for c in range(cols):
            val = resized[r, c]
            idx = int((255 - val) / 255.0 * (len(RAMP) - 1))
            idx = max(0, min(idx, len(RAMP) - 1))
            line_chars.append(RAMP[idx])
        # Escape for XML
        line_str = "".join(line_chars).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        lines.append(line_str)

    # SVG layout calculations to fit exactly 370x490
    view_w = 370
    view_h = 490
    
    row_w = cols * char_w  # 336
    padding_x = (view_w - row_w) / 2.0  # 17.0
    padding_y = (view_h - (rows * char_h)) / 2.0  # 32.5

    print(f"SVG Dimensions: viewBox='0 0 {view_w} {view_h}'")

    # Animation config
    stagger = 0.038  # Stagger delay between lines
    row_dur = 0.16   # Duration for a single row to wipe

    clip_paths = []
    text_lines = []
    cursors = []

    for idx, line in enumerate(lines):
        y = padding_y + idx * char_h
        y_text = y + char_h - 1.5  # Adjust baseline
        start_time = idx * stagger

        # Define clip path
        clip_paths.append(f"""    <clipPath id="clip-row-{idx}">
      <rect x="{padding_x}" y="{y}" width="0" height="{char_h}">
        <animate attributeName="width" from="0" to="{row_w}" dur="{row_dur}s" begin="{start_time:.3f}s" fill="freeze" />
      </rect>
    </clipPath>""")

        # Define text line
        text_lines.append(f'  <text x="{padding_x}" y="{y_text:.2f}" class="ascii-text" clip-path="url(#clip-row-{idx})">{line}</text>')

        # Define cursor riding the wipe edge
        cursors.append(f"""  <rect x="{padding_x}" y="{y}" width="{char_w}" height="{char_h}" class="cursor">
    <animate attributeName="x" from="{padding_x}" to="{padding_x + row_w}" dur="{row_dur}s" begin="{start_time:.3f}s" fill="freeze" />
    <animate attributeName="visibility" from="visible" to="hidden" begin="{start_time + row_dur:.3f}s" fill="freeze" />
  </rect>""")

    # SVG string
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" width="100%" height="100%">
  <style>
    .ascii-text {{
      font-family: 'Fira Code', 'Courier New', Courier, monospace;
      font-size: 8px;
      fill: #10b981;
      font-weight: bold;
    }}
    .cursor {{
      fill: #10b981;
    }}
  </style>
  <rect width="100%" height="100%" fill="#0b0f19" rx="8" stroke="#1f2937" stroke-width="1.5"/>
  <defs>
{chr(10).join(clip_paths)}
  </defs>

{chr(10).join(text_lines)}

{chr(10).join(cursors)}
</svg>
"""

    with open(output_path, "w") as f:
        f.write(svg_content)

    print(f"Successfully generated ASCII SVG: {output_path}")

if __name__ == "__main__":
    main()

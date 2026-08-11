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

    # Grid configuration to fit 370x490 card with 10px font size
    cols = 65
    rows = 45
    font_size = 10.0
    char_w = 5.2
    char_h = 10.0
    
    # Target physical aspect ratio of the grid
    target_aspect = (cols * char_w) / (rows * char_h)  # 338.0 / 450.0 = 0.7511

    # Crop prepped image to match target aspect ratio around center
    img_h, img_w = img.shape
    current_aspect = img_w / img_h
    if current_aspect > target_aspect:
        new_w = int(img_h * target_aspect)
        start_x = (img_w - new_w) // 2
        img = img[:, start_x:start_x+new_w]
    else:
        new_h = int(img_w / target_aspect)
        start_y = (img_h - new_h) // 2
        img = img[start_y:start_y+new_h, :]

    resized = cv2.resize(img, (cols, rows), interpolation=cv2.INTER_AREA)

    # ASCII character density ramp
    RAMP = " .:-=+*#%@"

    lines = []
    for r in range(rows):
        line_chars = []
        for c in range(cols):
            val = resized[r, c]
            if val >= 210:
                line_chars.append(" ")
            else:
                norm = (210.0 - val) / 210.0
                curved = np.power(norm, 1.1)
                idx = int(curved * (len(RAMP) - 1)) + 1
                idx = min(idx, len(RAMP) - 1)
                line_chars.append(RAMP[idx])
        # Escape for XML
        line_str = "".join(line_chars).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        lines.append(line_str)

    # SVG layout calculations
    view_w = 370
    view_h = 490
    
    row_w = cols * char_w  # 338.0
    padding_x = (view_w - row_w) / 2.0  # 16.0
    padding_y = (view_h - (rows * char_h)) / 2.0  # 20.0

    # Animation config
    stagger = 0.038  # Stagger delay between lines
    row_dur = 0.16   # Duration for a single row to wipe

    clip_paths = []
    text_lines = []
    cursors = []

    for idx, line in enumerate(lines):
        y = padding_y + idx * char_h
        y_text = y + char_h - 1.5  # Baseline offset
        start_time = idx * stagger

        # Define clip path
        clip_paths.append(f"""    <clipPath id="clip-row-{idx}">
      <rect x="{padding_x:.2f}" y="{y:.2f}" width="0" height="{char_h:.2f}">
        <animate attributeName="width" from="0" to="{row_w:.2f}" dur="{row_dur:.2f}s" begin="{start_time:.3f}s" fill="freeze" />
      </rect>
    </clipPath>""")

        # Define text line with xml:space="preserve"
        text_lines.append(f'  <text x="{padding_x:.2f}" y="{y_text:.2f}" class="ascii-text" clip-path="url(#clip-row-{idx})" xml:space="preserve">{line}</text>')

        # Define cursor riding the wipe edge
        cursors.append(f"""  <rect x="{padding_x:.2f}" y="{y:.2f}" width="{char_w:.2f}" height="{char_h:.2f}" class="cursor">
    <animate attributeName="x" from="{padding_x:.2f}" to="{(padding_x + row_w):.2f}" dur="{row_dur:.2f}s" begin="{start_time:.3f}s" fill="freeze" />
    <animate attributeName="visibility" from="visible" to="hidden" begin="{(start_time + row_dur):.3f}s" fill="freeze" />
  </rect>""")

    # SVG string
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" width="100%" height="100%">
  <style>
    .ascii-text {{
      font-family: 'ui-monospace', 'Cascadia Code', 'Source Code Pro', 'Menlo', 'Consolas', 'Courier New', monospace;
      font-size: {font_size}px;
      fill: #10b981;
      font-weight: bold;
      letter-spacing: 0px;
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

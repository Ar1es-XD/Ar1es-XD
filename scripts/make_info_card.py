import os

def html_escape(text):
    if not isinstance(text, str):
        return text
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")

def main():
    is_static = os.getenv("STATIC") == "1"

    width = 430
    height = 430
    output_path = "info-card.svg"

    # Define content lines (kept concise to prevent any right-edge cutoff)
    lines = [
        ('header', 'ar1es-xd@github'),
        ('divider', '--------------------'),
        ('kv', ('OS', 'macOS Sequoia 15.0')),
        ('kv', ('Host', 'GitHub Profile')),
        ('kv', ('Kernel', 'Darwin 24.0.0 (Apple Silicon)')),
        ('kv', ('Shell', 'zsh 5.9')),
        ('kv', ('Focus', 'Distributed Systems / AI Agents')),
        ('kv', ('Now', 'Training ESM-Mamba & AI codebots')),
        ('kv', ('Prev', 'Full-stack & automation dev')),
        ('kv', ('Stack', 'Python, JS/TS, Next.js, PyTorch')),
        ('kv', ('Projects', 'Algora, EmpowerMe, Task Tracker')),
        ('kv', ('Status', 'Active (clean state, 0 errors)')),
        ('divider', '--------------------'),
        ('quote', ('"Truth is ever to be found in simplicity,"', '"and not in confusion." — Sir Isaac Newton')),
        ('colors', None)
    ]

    # Generate CSS animation delays
    delays_css = []
    if not is_static:
        for idx in range(len(lines)):
            delays_css.append(f"      .line-{idx} {{ animation-delay: {0.08 + idx * 0.07:.2f}s; }}")
    else:
        delays_css.append("      .animate-line { opacity: 1 !important; animation: none !important; }")

    # Build lines SVG XML
    y_start = 32
    y_step = 22
    svg_elements = []

    for idx, item in enumerate(lines):
        item_type = item[0]
        y_pos = y_start + idx * y_step

        if item_type == 'header':
            svg_elements.append(f'  <g class="animate-line line-{idx}">')
            svg_elements.append(f'    <text x="20" y="{y_pos}" class="title">ar1es-xd</text>')
            svg_elements.append(f'    <text x="92" y="{y_pos}" class="val">@</text>')
            svg_elements.append(f'    <text x="104" y="{y_pos}" class="title">github</text>')
            svg_elements.append(f'  </g>')
        
        elif item_type == 'divider':
            svg_elements.append(f'  <g class="animate-line line-{idx}">')
            svg_elements.append(f'    <text x="20" y="{y_pos}" class="divider">{html_escape(item[1])}</text>')
            svg_elements.append(f'  </g>')
            
        elif item_type == 'kv':
            key, val = item[1]
            svg_elements.append(f'  <g class="animate-line line-{idx}">')
            svg_elements.append(f'    <text x="20" y="{y_pos}" class="key">{html_escape(key)}:</text>')
            svg_elements.append(f'    <text x="105" y="{y_pos}" class="val">{html_escape(val)}</text>')
            svg_elements.append(f'  </g>')

        elif item_type == 'quote':
            q1, q2 = item[1]
            svg_elements.append(f'  <g class="animate-line line-{idx}">')
            svg_elements.append(f'    <text x="20" y="{y_pos}" class="quote">{html_escape(q1)}</text>')
            svg_elements.append(f'    <text x="20" y="{y_pos + 16}" class="quote">{html_escape(q2)}</text>')
            svg_elements.append(f'  </g>')

        elif item_type == 'colors':
            y_pos_colors = y_pos + 16
            color_blocks = [
                "#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0", "#10b981", "#e65f2b"
            ]
            svg_elements.append(f'  <g class="animate-line line-{idx}">')
            for c_idx, color in enumerate(color_blocks):
                x_pos = 20 + c_idx * 26
                svg_elements.append(f'    <rect x="{x_pos}" y="{y_pos_colors}" width="20" height="13" fill="{color}" rx="2"/>')
            svg_elements.append(f'  </g>')

    # SVG layout
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <style>
    .title {{ font-family: 'Fira Code', monospace; font-size: 14px; font-weight: bold; fill: #10b981; }}
    .key {{ font-family: 'Fira Code', monospace; font-size: 12px; font-weight: bold; fill: #10b981; }}
    .val {{ font-family: 'Fira Code', monospace; font-size: 12px; fill: #cbd5e1; }}
    .divider {{ font-family: 'Fira Code', monospace; font-size: 12px; fill: #30363d; }}
    .quote {{ font-family: 'Fira Code', monospace; font-size: 11px; fill: #e65f2b; font-style: italic; }}
    
    @keyframes fadeInSlide {{
      from {{ opacity: 0; transform: translateY(6px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    .animate-line {{
      opacity: 0;
      animation: fadeInSlide 0.35s ease-out forwards;
    }}
{chr(10).join(delays_css)}
  </style>

  <rect width="100%" height="100%" fill="#0b0f19" rx="8" stroke="#1f2937" stroke-width="1.5"/>

{chr(10).join(svg_elements)}
</svg>
"""

    with open(output_path, "w") as f:
        f.write(svg_content)

    print(f"Successfully generated info card SVG: {output_path}")

if __name__ == "__main__":
    main()

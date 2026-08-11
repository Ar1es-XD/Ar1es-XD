import os

def main():
    is_static = os.getenv("STATIC") == "1"

    width = 490
    height = 490
    output_path = "info-card.svg"

    # Define content lines
    # Format: (type, content) -> type can be 'header', 'divider', 'kv', 'quote', 'colors'
    lines = [
        ('header', 'ar1es-xd@github'),
        ('divider', '---------------------'),
        ('kv', ('OS', 'macOS Sequoia (Darwin 24.0.0)')),
        ('kv', ('Host', 'GitHub Profile')),
        ('kv', ('Kernel', 'Antigravity AI Engine v3.5 (Flash)')),
        ('kv', ('Shell', 'zsh 5.9')),
        ('kv', ('Focus', 'Distributed Systems / ML Agents')),
        ('kv', ('Now', 'Training ESM-Mamba & building AI codebots')),
        ('kv', ('Prev', 'Full-stack web dev & automation engineer')),
        ('kv', ('Stack', 'Python, JS/TS, Next.js, Postgres, PyTorch, Docker')),
        ('kv', ('Projects', 'Algora, EmpowerMe, Task Tracker, ESM-Mamba')),
        ('kv', ('Status', 'Active (clean state, deterministic commits)')),
        ('divider', '---------------------'),
        ('quote', ('"Truth is ever to be found in simplicity, and not in the"', '"multiplicity and confusion of things." — Sir Isaac Newton')),
        ('colors', None)
    ]

    # Generate CSS animation delays
    delays_css = []
    if not is_static:
        for idx in range(len(lines)):
            # Special handling for quote since it might occupy multiple indices or lines
            delays_css.append(f"      .line-{idx} {{ animation-delay: {0.1 + idx * 0.08:.2f}s; }}")
    else:
        delays_css.append("      .animate-line { opacity: 1 !important; animation: none !important; }")

    # Build lines SVG XML
    y_start = 35
    y_step = 25
    svg_elements = []

    for idx, item in enumerate(lines):
        item_type = item[0]
        y_pos = y_start + idx * y_step

        if item_type == 'header':
            svg_elements.append(f'  <g class="animate-line line-{idx}">')
            svg_elements.append(f'    <text x="25" y="{y_pos}" class="title">ar1es-xd</text>')
            svg_elements.append(f'    <text x="97" y="{y_pos}" class="val">@</text>')
            svg_elements.append(f'    <text x="109" y="{y_pos}" class="title">github</text>')
            svg_elements.append(f'  </g>')
        
        elif item_type == 'divider':
            svg_elements.append(f'  <g class="animate-line line-{idx}">')
            svg_elements.append(f'    <text x="25" y="{y_pos}" class="divider">{item[1]}</text>')
            svg_elements.append(f'  </g>')
            
        elif item_type == 'kv':
            key, val = item[1]
            svg_elements.append(f'  <g class="animate-line line-{idx}">')
            svg_elements.append(f'    <text x="25" y="{y_pos}" class="key">{key}:</text>')
            svg_elements.append(f'    <text x="120" y="{y_pos}" class="val">{val}</text>')
            svg_elements.append(f'  </g>')

        elif item_type == 'quote':
            q1, q2 = item[1]
            svg_elements.append(f'  <g class="animate-line line-{idx}">')
            svg_elements.append(f'    <text x="25" y="{y_pos}" class="quote">{q1}</text>')
            svg_elements.append(f'    <text x="25" y="{y_pos + 18}" class="quote">{q2}</text>')
            svg_elements.append(f'  </g>')

        elif item_type == 'colors':
            y_pos_colors = y_pos + 20
            color_blocks = [
                "#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0", "#10b981", "#e65f2b"
            ]
            svg_elements.append(f'  <g class="animate-line line-{idx}">')
            for c_idx, color in enumerate(color_blocks):
                x_pos = 25 + c_idx * 28
                svg_elements.append(f'    <rect x="{x_pos}" y="{y_pos_colors}" width="22" height="15" fill="{color}" rx="2"/>')
            svg_elements.append(f'  </g>')

    # SVG layout
    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="100%" height="100%">
  <style>
    .title {{ font-family: 'Fira Code', monospace; font-size: 15px; font-weight: bold; fill: #10b981; }}
    .key {{ font-family: 'Fira Code', monospace; font-size: 13px; font-weight: bold; fill: #10b981; }}
    .val {{ font-family: 'Fira Code', monospace; font-size: 13px; fill: #cbd5e1; }}
    .divider {{ font-family: 'Fira Code', monospace; font-size: 13px; fill: #30363d; }}
    .quote {{ font-family: 'Fira Code', monospace; font-size: 12px; fill: #e65f2b; font-style: italic; }}
    
    @keyframes fadeInSlide {{
      from {{ opacity: 0; transform: translateY(8px); }}
      to {{ opacity: 1; transform: translateY(0); }}
    }}
    .animate-line {{
      opacity: 0;
      animation: fadeInSlide 0.4s ease-out forwards;
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

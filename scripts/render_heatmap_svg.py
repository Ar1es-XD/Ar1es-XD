import json
import os
import sys
from datetime import datetime

def main():
    json_path = "data/contributions.json"
    output_path = "contrib-heatmap.svg"

    if not os.path.exists(json_path):
        print(f"Error: {json_path} does not exist. Run fetch_contributions.py first.")
        sys.exit(1)

    with open(json_path, "r") as f:
        data = json.load(f)

    days = data["days"]
    total = data["total"]
    current_streak = data["current_streak"]
    longest_streak = data["longest_streak"]
    best_day = data["best_day"]

    # Configs matching exactly 860px width
    view_w = 860
    view_h = 200
    box_size = 12
    gap = 2.8
    padding_left = 30
    padding_top = 35

    # Palette
    PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]

    if not days:
        print("Error: No days found in contribution data.")
        sys.exit(1)

    first_date_str = days[0]["date"]
    first_date = datetime.strptime(first_date_str, "%Y-%m-%d")
    first_wday = (first_date.weekday() + 1) % 7

    rect_elements = []
    seen_months = set()
    month_labels = []

    for idx, day in enumerate(days):
        d = datetime.strptime(day["date"], "%Y-%m-%d")
        col_idx = (idx + first_wday) // 7
        row_idx = (idx + first_wday) % 7

        x = padding_left + col_idx * (box_size + gap)
        y = padding_top + row_idx * (box_size + gap)

        level = day["level"]
        count = day["count"]
        
        level_idx = level
        if level == 4 and count >= 10:
            level_idx = 5
        level_idx = max(0, min(level_idx, len(PALETTE) - 1))
        color = PALETTE[level_idx]

        delay = (col_idx + row_idx) * 0.014

        rect_elements.append(
            f'  <rect x="{x:.2f}" y="{y:.2f}" width="{box_size}" height="{box_size}" rx="2" fill="{color}" class="day-rect" style="animation-delay: {delay:.3f}s;"/>'
        )

        month_name = d.strftime("%b")
        year_month = d.strftime("%Y-%m")
        if year_month not in seen_months:
            seen_months.add(year_month)
            month_labels.append((col_idx, month_name))

    month_elements = []
    last_label_col = -5
    for col_idx, name in month_labels:
        if col_idx - last_label_col >= 3 and col_idx < 52:
            x = padding_left + col_idx * (box_size + gap)
            y = padding_top - 8
            month_elements.append(f'  <text x="{x:.2f}" y="{y:.2f}" class="legend-text">{name}</text>')
            last_label_col = col_idx

    day_labels = [("Mon", 1), ("Wed", 3), ("Fri", 5)]
    day_elements = []
    for label, row_idx in day_labels:
        y = padding_top + row_idx * (box_size + gap) + 9
        x = padding_left - 6
        day_elements.append(f'  <text x="{x:.2f}" y="{y:.2f}" class="legend-text" text-anchor="end">{label}</text>')

    legend_elements = []
    legend_x_start = 685
    legend_y = 145
    legend_elements.append(f'  <text x="{legend_x_start}" y="{legend_y + 9}" class="legend-text">Less</text>')
    
    for c_idx, color in enumerate(PALETTE):
        rx = legend_x_start + 30 + c_idx * (box_size + 2)
        legend_elements.append(
            f'  <rect x="{rx:.2f}" y="{legend_y:.2f}" width="{box_size}" height="{box_size}" rx="2" fill="{color}"/>'
        )
    
    legend_elements.append(
        f'  <text x="{legend_x_start + 30 + len(PALETTE) * (box_size + 2) + 4}" y="{legend_y + 9}" class="legend-text">More</text>'
    )

    stats_left = f"{total:,} contributions in the last year"
    best_day_date = datetime.strptime(best_day["date"], "%Y-%m-%d").strftime("%B %d, %Y") if best_day["date"] else ""
    best_day_str = f"Best: {best_day['count']} ({best_day_date})" if best_day["count"] > 0 else ""
    
    stats_right = f"Streak: {current_streak} days (Max: {longest_streak} days)"
    if best_day_str:
        stats_right = f"{stats_right} | {best_day_str}"

    svg_content = f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {view_w} {view_h}" width="100%" height="100%">
  <style>
    .legend-text {{
      font-family: 'Fira Code', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 9px;
      fill: #8b949e;
    }}
    .stat-text {{
      font-family: 'Fira Code', -apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif;
      font-size: 11px;
      fill: #cbd5e1;
    }}
    .day-rect {{
      opacity: 0;
      animation: slideIn 0.35s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
    @keyframes slideIn {{
      from {{
        opacity: 0;
        transform: translateY(-6px);
      }}
      to {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}
  </style>

  <rect width="100%" height="100%" fill="#0b0f19" rx="8" stroke="#1f2937" stroke-width="1.5"/>

  <!-- Month Labels -->
{chr(10).join(month_elements)}

  <!-- Day Labels -->
{chr(10).join(day_elements)}

  <!-- Contribution Grid -->
{chr(10).join(rect_elements)}

  <!-- Legend -->
{chr(10).join(legend_elements)}

  <!-- Stats Footer -->
  <line x1="20" y1="165" x2="{view_w - 20}" y2="165" stroke="#1f2937" stroke-width="1"/>
  <text x="30" y="180" class="stat-text">{stats_left}</text>
  <text x="{view_w - 30}" y="180" class="stat-text" text-anchor="end">{stats_right}</text>
</svg>
"""

    with open(output_path, "w") as f:
        f.write(svg_content)

    print(f"Successfully rendered contribution heatmap to {output_path}")

if __name__ == "__main__":
    main()

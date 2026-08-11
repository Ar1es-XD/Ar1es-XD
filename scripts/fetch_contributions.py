import os
import sys
import re
import json
import requests
from bs4 import BeautifulSoup

def main():
    username = "Ar1es-XD"
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    print(f"Fetching contributions from: {url}")
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Error: Failed to fetch page. Status: {response.status_code}")
        sys.exit(1)
        
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract all tooltips by their target element ID
    tooltips = {}
    for tt in soup.find_all('tool-tip'):
        if tt.has_attr('for'):
            tooltips[tt['for']] = tt.get_text().strip()
            
    # Find all day cells
    days_data = []
    total_contributions = 0
    best_day = {"date": "", "count": -1}
    
    # Find all cells with data-date attribute
    day_cells = soup.find_all(attrs={"data-date": True})
    
    for cell in day_cells:
        date = cell['data-date']
        level = int(cell.get('data-level', 0))
        cell_id = cell.get('id', '')
        
        # Get count from tooltip
        tooltip_text = tooltips.get(cell_id, "")
        count = 0
        if "No contributions" in tooltip_text or tooltip_text == "":
            count = 0
        else:
            # Matches strings like "5 contributions on August 12, 2025" or "1 contribution on ..."
            match = re.match(r"^([0-9,]+)\s+contribution", tooltip_text)
            if match:
                count = int(match.group(1).replace(',', ''))
                
        total_contributions += count
        if count > best_day["count"]:
            best_day = {"date": date, "count": count}
            
        days_data.append({
            "date": date,
            "count": count,
            "level": level
        })
        
    # Sort days chronologically
    days_data.sort(key=lambda x: x["date"])
    
    # Calculate streaks
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    
    # Longest streak calculation
    for day in days_data:
        if day["count"] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0
            
    # Current streak calculation: count backwards from the last day in the list
    reversed_days = list(reversed(days_data))
    if len(reversed_days) > 0:
        active_found = False
        streak_count = 0
        for i, d in enumerate(reversed_days):
            if d["count"] > 0:
                active_found = True
                streak_count += 1
            else:
                if active_found:
                    # We already started counting a streak, but hit a 0, so the streak ends
                    break
                else:
                    # We haven't found an active day yet.
                    # Allow today (index 0) to be 0 without breaking the streak.
                    if i >= 1:
                        # More than 1 day of 0s at the end breaks the streak.
                        break
        current_streak = streak_count
    
    # Calculate monthly totals
    monthly_totals = {}
    for day in days_data:
        month_key = day["date"][:7]  # YYYY-MM
        monthly_totals[month_key] = monthly_totals.get(month_key, 0) + day["count"]
        
    output_data = {
        "username": username,
        "total": total_contributions,
        "best_day": best_day,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "monthly_totals": monthly_totals,
        "days": days_data
    }
    
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)
    with open("data/contributions.json", "w") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"Saved contributions for {username}. Total: {total_contributions}. Current streak: {current_streak}. Longest streak: {longest_streak}.")

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Check GitHub profile for new achievements and notify via issue creation."""
import json
import os
import re
import sys
import urllib.request

USERNAME = "Ar1es-XD"
BASELINE_FILE = "data/achievements_baseline.json"

# Known GitHub achievement names to track
TRACKABLE = [
    "Quickdraw",
    "YOLO",
    "Pull Shark",
    "Galaxy Brain",
]


def fetch_profile_achievements():
    """Scrape the GitHub profile page for achievement badge names."""
    url = f"https://github.com/{USERNAME}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            html = resp.read().decode("utf-8", errors="replace")
    except Exception as e:
        print(f"Failed to fetch profile: {e}")
        return None

    # GitHub renders achievements in img alt text and aria-label attributes
    found = set()
    for name in TRACKABLE:
        # Match achievement names in alt="Achievement: Pull Shark" or similar patterns
        patterns = [
            rf'alt="[^"]*{re.escape(name)}[^"]*"',
            rf'aria-label="[^"]*{re.escape(name)}[^"]*"',
            rf'>{re.escape(name)}<',
            rf'title="[^"]*{re.escape(name)}[^"]*"',
        ]
        for pat in patterns:
            if re.search(pat, html, re.IGNORECASE):
                found.add(name)
                break

    return found


def load_baseline():
    """Load the previously seen achievements."""
    if not os.path.exists(BASELINE_FILE):
        return set()
    with open(BASELINE_FILE, "r") as f:
        data = json.load(f)
    return set(data.get("seen", []))


def save_baseline(seen):
    """Save the current set of seen achievements."""
    os.makedirs(os.path.dirname(BASELINE_FILE), exist_ok=True)
    with open(BASELINE_FILE, "w") as f:
        json.dump({"seen": sorted(seen)}, f, indent=2)


def create_notification_issue(achievement_name):
    """Create a GitHub issue to trigger an email notification."""
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        print(f"  No GITHUB_TOKEN — skipping issue for {achievement_name}")
        return

    body = json.dumps({
        "title": f"🏆 Achievement Unlocked: {achievement_name}",
        "body": (
            f"**{achievement_name}** is now visible on your "
            f"[GitHub profile](https://github.com/{USERNAME})!\n\n"
            f"This issue was auto-created by the achievement tracker workflow. "
            f"You can close it."
        ),
        "labels": ["achievement"],
    }).encode("utf-8")

    url = f"https://api.github.com/repos/{USERNAME}/{USERNAME}/issues"
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "User-Agent": "AchievementTracker/1.0",
    })
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            result = json.loads(resp.read())
            print(f"  ✅ Created issue #{result['number']}: {achievement_name}")
    except Exception as e:
        print(f"  ❌ Failed to create issue for {achievement_name}: {e}")


def main():
    print(f"Checking achievements for {USERNAME}...")
    current = fetch_profile_achievements()
    if current is None:
        print("Could not fetch profile. Exiting.")
        sys.exit(1)

    print(f"Found on profile: {current or '(none yet)'}")
    baseline = load_baseline()
    print(f"Previously seen:  {baseline or '(none)'}")

    new_achievements = current - baseline
    if new_achievements:
        print(f"\n🎉 NEW achievements detected: {new_achievements}")
        for name in sorted(new_achievements):
            create_notification_issue(name)
        save_baseline(current | baseline)
    else:
        print("\nNo new achievements yet. Will check again later.")
        # Still save current state so baseline stays accurate
        save_baseline(current | baseline)


if __name__ == "__main__":
    main()

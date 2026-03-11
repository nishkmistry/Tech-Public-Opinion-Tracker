import requests
import pandas as pd
import time
import os
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIGURATION
# ─────────────────────────────────────────────
SUBREDDIT = "technology"
OUTPUT_FILE = "data/raw_posts.csv"
DELAY = 2  # seconds between requests

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36"
}

os.makedirs("data", exist_ok=True)

# ─────────────────────────────────────────────
# FETCH ONE PAGE OF POSTS
# ─────────────────────────────────────────────
def fetch_page(category, after=None, time_filter=None):
    params = {"limit": 100, "raw_json": 1}
    if after:
        params["after"] = after
    if time_filter:
        params["t"] = time_filter

    url = f"https://www.reddit.com/r/{SUBREDDIT}/{category}.json"

    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=15)
        if response.status_code == 200:
            return response.json()
        elif response.status_code == 429:
            print("    ⚠️ Rate limited! Waiting 60 seconds...")
            time.sleep(60)
            return fetch_page(category, after, time_filter)
        else:
            print(f"    ❌ HTTP {response.status_code}")
            return None
    except Exception as e:
        print(f"    ❌ Error: {e}")
        return None


# ─────────────────────────────────────────────
# PARSE POSTS FROM RESPONSE
# ─────────────────────────────────────────────
def parse_posts(data, category, time_filter=None):
    posts = []
    if not data or "data" not in data:
        return posts, None

    children = data["data"].get("children", [])
    after = data["data"].get("after", None)

    for child in children:
        p = child.get("data", {})
        # Skip deleted/removed posts
        if p.get("title", "") in ["", "[deleted]", "[removed]"]:
            continue
        posts.append({
            "id":           p.get("id", ""),
            "title":        p.get("title", ""),
            "body":         p.get("selftext", ""),
            "score":        p.get("score", 0),
            "upvote_ratio": p.get("upvote_ratio", 0),
            "num_comments": p.get("num_comments", 0),
            "flair":        p.get("link_flair_text", ""),
            "author":       p.get("author", ""),
            "url":          p.get("url", ""),
            "permalink":    "https://reddit.com" + p.get("permalink", ""),
            "created_utc":  datetime.fromtimestamp(
                                p.get("created_utc", 0)
                            ).strftime("%Y-%m-%d %H:%M:%S"),
            "category":     f"{category}_{time_filter}" if time_filter else category,
            "is_self_post": p.get("is_self", False),
            "domain":       p.get("domain", ""),
        })

    return posts, after


# ─────────────────────────────────────────────
# SCRAPE ONE CATEGORY/TIME FILTER COMBO
# ─────────────────────────────────────────────
def scrape_category(category, time_filter=None, max_pages=10, seen_ids=None):
    if seen_ids is None:
        seen_ids = set()

    label = f"{category}/{time_filter}" if time_filter else category
    print(f"\n📂 Fetching '{label}'...")

    all_posts = []
    after = None

    for page in range(max_pages):
        data = fetch_page(category, after=after, time_filter=time_filter)
        if not data:
            print(f"   No data returned, stopping.")
            break

        posts, after = parse_posts(data, category, time_filter)
        if not posts:
            print(f"   Empty page, stopping.")
            break

        # Only add posts we haven't seen
        new_posts = [p for p in posts if p["id"] not in seen_ids]
        for p in new_posts:
            seen_ids.add(p["id"])

        all_posts.extend(new_posts)
        print(f"   Page {page+1}: +{len(new_posts)} new | Running total this category: {len(all_posts)}")

        if not after:
            print(f"   No more pages.")
            break

        time.sleep(DELAY)

    print(f"   ✅ Done: {len(all_posts)} posts")
    return all_posts, seen_ids


# ─────────────────────────────────────────────
# FETCH TOP COMMENTS
# ─────────────────────────────────────────────
def fetch_comments(permalink, n=5):
    url = permalink.rstrip("/") + ".json"
    try:
        response = requests.get(
            url, headers=HEADERS,
            params={"limit": n, "raw_json": 1},
            timeout=10
        )
        if response.status_code != 200:
            return ""
        data = response.json()
        comments = []
        if len(data) > 1:
            for child in data[1]["data"]["children"][:n]:
                body = child.get("data", {}).get("body", "")
                if body and body not in ["[deleted]", "[removed]"]:
                    comments.append(body.strip())
        return " | ".join(comments)
    except:
        return ""


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    all_posts = []
    seen_ids = set()

    print(f"🚀 Scraping r/{SUBREDDIT}")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")

    # --- HOT (paginate through 10 pages = up to 1000 posts) ---
    posts, seen_ids = scrape_category("hot", max_pages=10, seen_ids=seen_ids)
    all_posts.extend(posts)

    # --- TOP by different time filters (completely different posts) ---
    for time_filter in ["week", "month", "year", "all"]:
        posts, seen_ids = scrape_category("top", time_filter=time_filter, max_pages=5, seen_ids=seen_ids)
        all_posts.extend(posts)

    # --- NEW (recent posts, mostly unique from hot/top) ---
    posts, seen_ids = scrape_category("new", max_pages=5, seen_ids=seen_ids)
    all_posts.extend(posts)

    print(f"\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"📊 Total unique posts scraped: {len(all_posts)}")

    # ─────────────────────────────────────────
    # FETCH COMMENTS
    # ─────────────────────────────────────────
    print(f"\n💬 Fetching top comments...")
    print(f"   Estimated time: ~{len(all_posts) * DELAY / 60:.0f} mins")

    for i, post in enumerate(all_posts):
        if i % 200 == 0:
            print(f"   Progress: {i}/{len(all_posts)} posts")
        post["top_comments"] = fetch_comments(post["permalink"], n=5)
        time.sleep(DELAY)

    # ─────────────────────────────────────────
    # BUILD DATAFRAME & SAVE
    # ─────────────────────────────────────────
    df = pd.DataFrame(all_posts)
    df = df[df["title"].str.len() > 0].reset_index(drop=True)

    # Combined text for NLP
    df["full_text"] = (
        df["title"].fillna("") + " " +
        df["body"].fillna("") + " " +
        df["top_comments"].fillna("")
    ).str.strip()

    df.to_csv(OUTPUT_FILE, index=False)

    # ─────────────────────────────────────────
    # FINAL STATS
    # ─────────────────────────────────────────
    print(f"\n✅ SCRAPING COMPLETE!")
    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print(f"Total posts saved : {len(df)}")
    print(f"Columns           : {list(df.columns)}")
    print(f"Saved to          : {OUTPUT_FILE}")
    print(f"\n📂 Category breakdown:")
    print(df["category"].value_counts().to_string())
    print(f"\n🏷️  Top flairs:")
    print(df["flair"].value_counts().head(10).to_string())
    print(f"\n📅 Date range:")
    print(f"   {df['created_utc'].min()} → {df['created_utc'].max()}")
    print(f"\n🔢 Sample titles:")
    for t in df["title"].sample(5).values:
        print(f"   • {t[:90]}")

    return df


if __name__ == "__main__":
    df = main()
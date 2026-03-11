import requests
import pandas as pd
import datetime
import time

def fetch_reddit_data(subreddit, limit=1000):
    url = f"https://www.reddit.com/r/technology/top.json"
    headers = {"User-Agent": "windows:tech_opinion_tracker:v1.0"}
    posts = []
    after = None
    
    while len(posts) < limit:
        params = {"limit": 100, "t": "month"}
        if after:
            params["after"] = after
            
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code != 200:
            break
            
        data = response.json()
        children = data.get("data", {}).get("children", [])
        
        if not children:
            break
            
        for child in children:
            post = child["data"]
            posts.append([
                post.get("title", ""),
                post.get("selftext", ""),
                post.get("score", 0),
                post.get("num_comments", 0),
                datetime.datetime.fromtimestamp(post.get("created_utc", 0)),
                post.get("subreddit", subreddit)
            ])
            
        after = data.get("data", {}).get("after")
        if not after:
            break
            
        time.sleep(2)
        
    return pd.DataFrame(posts[:limit], columns=["title", "body", "upvotes", "comment_count", "timestamp", "subreddit"])

df = fetch_reddit_data("technology", 1000)
df.to_csv("reddit_technology_data.csv", index=False)
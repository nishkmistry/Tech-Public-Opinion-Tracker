import os
import time
import pandas as pd
import requests

def scrape_category(category, limit_per_request=100, max_posts=1000):
    """
    Scrapes a specific category (hot, top/week, top/month, top/year, top/all) 
    using Reddit's public JSON endpoint with pagination via the 'after' token.
    """
    posts = []
    after = None
    
    # Using a unique and descriptive User-Agent to avoid immediate 429 errors
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 TechPublicOpinionTracker/1.0'
    }
    
    session = requests.Session()
    session.headers.update(headers)
    
    # Parse sub-categories for 'top' (e.g., top/week -> category='top', t='week')
    url_category = category
    params = {'limit': limit_per_request}
    
    if 'top/' in category:
        url_category = 'top'
        params['t'] = category.split('/')[1]

    url = f"https://www.reddit.com/r/technology/{url_category}.json"
    
    print(f"🚀 Starting scrape for category: r/technology/{category}")
    
    while len(posts) < max_posts:
        if after:
            params['after'] = after
            
        try:
            response = session.get(url, params=params, timeout=15)
            
            if response.status_code == 429:
                print("⚠️ Rate limited (429). Backing off for 10 seconds...")
                time.sleep(10)
                continue
                
            if response.status_code != 200:
                print(f"❌ Failed to fetch data: HTTP {response.status_code}")
                break
                
            data = response.json()
            children = data.get('data', {}).get('children', [])
            
            if not children:
                print(f"ℹ️ No more posts found for {category}.")
                break
                
            for post in children:
                data_node = post.get('data', {})
                
                # Extracting all required fields as per your feature specifications
                posts.append({
                    'title': data_node.get('title', ''),
                    'body': data_node.get('selftext', ''),
                    'score': data_node.get('score', 0),
                    'upvote_ratio': data_node.get('upvote_ratio', 0.0),
                    'comment_count': data_node.get('num_comments', 0),
                    'flair': data_node.get('link_flair_text', 'None'),
                    'author': data_node.get('author', ''),
                    'timestamp': data_node.get('created_utc', time.time()),
                    'top_comments': "" # Left blank or can be parsed via separate endpoint if needed
                })
                
            print(f"✅ Fetched {len(posts)}/{max_posts} posts from {category}...")
            
            after = data.get('data', {}).get('after')
            if not after:
                break
                
            # A 2-second sleep per batch of 100 items is highly respectful and safe
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error encountered during extraction: {e}")
            break
            
    return posts

def main():
    # Targets corresponding exactly to your project categories
    categories = ['hot', 'top/week', 'top/month', 'top/year', 'top/all']
    all_posts = []
    
    for cat in categories:
        cat_posts = scrape_category(cat, limit_per_request=100, max_posts=600)
        all_posts.extend(cat_posts)
        time.sleep(3) # Small break between category swaps
        
    # Convert to DataFrame and drop duplicates based on title and timestamp
    df = pd.DataFrame(all_posts)
    if not df.empty:
        df = df.drop_duplicates(subset=['title', 'timestamp']).reset_index(drop=True)
        
        # Ensure target data directory exists
        os.makedirs('data', exist_ok=True)
        
        output_path = 'data/raw_posts.csv'
        df.to_csv(output_path, index=False)
        print(f"\n🎉 Extraction Complete! Successfully saved {len(df)} unique records to '{output_path}'.")
    else:
        print("\n❌ Pipeline Error: No elements extracted.")

if __name__ == "__main__":
    main()
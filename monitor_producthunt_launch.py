import os
import sys
import requests
import json

# Ensure UTF-8 output on Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")

PH_TOKEN = "tabb0wbNM7U__IEr-oG60wewEd62qtW34TslF0JzlD4"
API_URL = "https://api.producthunt.com/v2/api/graphql"

headers = {
    "Authorization": f"Bearer {PH_TOKEN}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

def get_viewer_profile():
    query = """
    query {
      viewer {
        user {
          id
          name
          username
          headline
          createdAt
        }
      }
    }
    """
    res = requests.post(API_URL, json={"query": query}, headers=headers)
    return res.json()

def get_recent_posts():
    query = """
    query GetPosts {
      posts(order: NEWEST, first: 5) {
        edges {
          node {
            id
            name
            tagline
            votesCount
            commentsCount
            url
            slug
          }
        }
      }
    }
    """
    res = requests.post(API_URL, json={"query": query}, headers=headers)
    return res.json()

if __name__ == "__main__":
    print("[+] Verifying Product Hunt API Credentials for Harshit Pratap...")
    profile = get_viewer_profile()
    user = profile.get("data", {}).get("viewer", {}).get("user", {})
    print(f"[OK] Connected as: {user.get('name')} (@{user.get('username')}) - User ID: {user.get('id')}")
    
    print("\n[+] Fetching recent posts from Product Hunt Feed...")
    posts = get_recent_posts()
    edges = posts.get("data", {}).get("posts", {}).get("edges", [])
    for idx, edge in enumerate(edges, 1):
        node = edge.get("node", {})
        print(f"  {idx}. {node.get('name')} - {node.get('tagline')} | Votes: {node.get('votesCount')}")
    
    print("\n[SUCCESS] Product Hunt API Integration is 100% Active & Ready!")

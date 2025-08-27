import requests
import json
import re
import sys
from tqdm import tqdm
import cookie
import os
import csv

# Configuration
PARENT_QUERY_HASH = "97b41c52301f77ce508f55e66d17620e"
COMMENTS_PER_PAGE = 50

# Cookies from cookie.py
sessionid = cookie.sessionid
ds_user_id = cookie.ds_user_id
csrftoken = cookie.csrftoken
mid = cookie.mid

def extract_shortcode(url):
    """
    Extract the shortcode from an Instagram URL.
    Works for /p/ (post), /reel/, or /tv/ (IGTV).
    """
    m = re.search(r"instagram\.com/(?:p|reel|tv)/([^/?]+)", url)
    return m.group(1) if m else None


def detect_content_type(url):
    """
    Detect the type of Instagram content from the URL.
    """
    if "/p/" in url:
        return "p"
    elif "/reel/" in url:
        return "reel"
    elif "/tv/" in url:
        return "tv"
    else:
        return "p"  # default to post


def build_headers(shortcode, cookies_str, content_type="p"):
    """
    Build request headers for Instagram GraphQL API.
    """
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                      "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept": "/",
        "Accept-Language": "en-US,en;q=0.9",
        "X-Requested-With": "XMLHttpRequest",
        "X-IG-App-ID": "936619743392459",
        "Referer": f"https://www.instagram.com/{content_type}/{shortcode}/",
        "Cookie": cookies_str
    }


def graphql_request(query_hash, variables, headers):
    """
    Send a GraphQL request to Instagram.
    """
    var_str = json.dumps(variables, separators=(",", ":"))
    url = (
        f"https://www.instagram.com/graphql/query/"
        f"?query_hash={query_hash}"
        f"&variables={requests.utils.quote(var_str)}"
    )
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        print(f"[!] HTTP {r.status_code} error for {query_hash}: {r.text}")
        sys.exit(1)
    return r.json()


def fetch_user_info(username, headers):
    """
    Fetch user profile info: follower, following, is_verified.
    """
    url = f"https://www.instagram.com/{username}/?__a=1&__d=dis"
    r = requests.get(url, headers=headers)
    if r.status_code != 200:
        return {"follower": "", "following": "", "is_verified": ""}
    try:
        user = r.json()["graphql"]["user"]
        return {
            "follower": user.get("edge_followed_by", {}).get("count", ""),
            "following": user.get("edge_follow", {}).get("count", ""),
            "is_verified": user.get("is_verified", False)
        }
    except Exception:
        return {"follower": "", "following": "", "is_verified": ""}

def fetch_parent_comments(shortcode, headers):
    """
    Fetch all parent comments (and their replies) from a post/reel.
    Handles pagination automatically until all comments are retrieved.
    """
    all_comments = []
    has_next = True
    cursor = ""
    page_count = 0

    progress_bar = tqdm(total=100, desc="Fetching Comments", unit="page")

    while has_next:
        vars = {"shortcode": shortcode, "first": COMMENTS_PER_PAGE}
        if cursor:
            vars["after"] = cursor

        data = graphql_request(PARENT_QUERY_HASH, vars, headers)

        try:
            edge_info = data["data"]["shortcode_media"]["edge_media_to_parent_comment"]
            edges = edge_info["edges"]
            for edge in edges:
                node = edge["node"]
                parent_id = node["id"]

                # parent comment
                all_comments.append({
                    "comment_id": parent_id,
                    "parent_id": "",
                    "username": node["owner"]["username"],
                    "comment": node["text"],
                    "comment_time": node.get("created_at", ""),
                    "like_count": node.get("edge_liked_by", {}).get("count", ""),
                    "reply_count": node.get("edge_threaded_comments", {}).get("count", "")
                })
            
                # child comments (replies)
                replies = node.get("edge_threaded_comments", {}).get("edges", [])
                for reply in replies:
                    reply_node = reply["node"]
                    all_comments.append({
                        "comment_id": reply_node["id"],
                        "parent_id": parent_id,
                        "username": reply_node["owner"]["username"],
                        "comment": reply_node["text"],
                        "comment_time": reply_node.get("created_at", ""),
                        "like_count": reply_node.get("edge_liked_by", {}).get("count", ""),
                        "reply_count": ""
                    })
        except KeyError as e:
            print(f"[!] Error parsing comment data: {e}")
            break

        page_info = edge_info["page_info"]
        has_next = page_info["has_next_page"]
        cursor = page_info["end_cursor"]

        page_count += 1
        progress_bar.n = page_count * COMMENTS_PER_PAGE
        progress_bar.last_print_n = progress_bar.n
        progress_bar.update(0)

    progress_bar.close()
    return all_comments

def main():
    insta_url = input("Enter Instagram Post/Reel URL: ").strip()

    shortcode = extract_shortcode(insta_url)
    if not shortcode:
        print("[!] Invalid URL format.")
        exit()

    content_type = detect_content_type(insta_url)

    cookies_str = f"sessionid={sessionid}; ds_user_id={ds_user_id}; csrftoken={csrftoken}; mid={mid};"
    headers = build_headers(shortcode, cookies_str, content_type)

    comments = fetch_parent_comments(shortcode, headers)

    # Ensure 'data' folder exists
    data_folder = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(data_folder, exist_ok=True)
    csv_path = os.path.join(data_folder, "comments.csv")

    if comments:
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "comment_id", "parent_id", "username", "comment", 
                "comment_time", "like_count", "reply_count"
            ])
            for c in comments:
                writer.writerow([
                    c["comment_id"], c["parent_id"], c["username"], c["comment"],
                    c["comment_time"], c["like_count"], c["reply_count"]
                ])
        print(f"[+] Saved {len(comments)} comments to {csv_path}")
    else:
        print("[!] No comments found or failed.")

if __name__ == "__main__":
    main()
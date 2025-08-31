import os
import httpx
import json

# Path where usage file will be stored — adjust if needed
# If your WP root is /var/www/html/wordpress, this will save in the same folder
USAGE_FILE = os.path.join(os.path.dirname(__file__), "..", "gcs_usage.json")

# --- Helper functions for quota tracking ---
def save_gcs_usage(count: int):
    try:
        with open(USAGE_FILE, "w") as f:
            json.dump({"count": count}, f)
    except Exception as e:
        print("Error saving GCS usage:", e)

def load_gcs_usage() -> int:
    try:
        if os.path.exists(USAGE_FILE):
            with open(USAGE_FILE, "r") as f:
                return json.load(f).get("count", 0)
    except Exception as e:
        print("Error loading GCS usage:", e)
    return 0

# Global counter (loads existing value if file exists)
gcs_usage_count = load_gcs_usage()

# --- DuckDuckGo Instant Answer ---
async def duckduckgo_instant_answer(query: str) -> str:
    """
    Query DuckDuckGo Instant Answer API.
    Returns abstract text + source URL if available.
    """
    url = "https://api.duckduckgo.com/"
    params = {
        "q": query,
        "format": "json",
        "no_html": 1,
        "skip_disambig": 1
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        data = resp.json()

    if data.get("AbstractText"):
        abstract = data["AbstractText"]
        source_url = data.get("AbstractURL", "")
        if source_url:
            return f"{abstract} ({source_url})"
        return abstract

    elif data.get("RelatedTopics"):
        for topic in data["RelatedTopics"]:
            if isinstance(topic, dict) and "Text" in topic:
                text = topic["Text"]
                first_url = topic.get("FirstURL", "")
                if first_url:
                    return f"{text} ({first_url})"
                return text

    return ""


# --- Google Custom Search ---
async def google_custom_search(query: str) -> str:
    """
    Query Google Custom Search JSON API.
    Returns top 3 results with title, snippet, and URL.
    Logs usage count so you can track quota.
    """
    global gcs_usage_count
    api_key = os.getenv("GCS_API_KEY")
    cx = os.getenv("GCS_CX")
    if not api_key or not cx:
        return "Google Custom Search API not configured."

    url = "https://www.googleapis.com/customsearch/v1"
    params = {"key": api_key, "cx": cx, "q": query}

    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        data = resp.json()

    if "items" not in data:
        return ""

    # Increment and save usage
    gcs_usage_count += 1
    save_gcs_usage(gcs_usage_count)

    results = []
    for item in data["items"][:3]:
        title = item.get("title", "")
        snippet = item.get("snippet", "")
        link = item.get("link", "")
        results.append(f"{title}: {snippet} ({link})")

    return "\n".join(results)


# --- Combined logic ---
async def get_web_context(query: str) -> str:
    """
    Try DuckDuckGo first (free, unlimited).
    If no answer, fall back to Google Custom Search (3,000/month free).
    """
    ddg_result = await duckduckgo_instant_answer(query)
    if ddg_result.strip():
        return f"DuckDuckGo says: {ddg_result}"

    gcs_result = await google_custom_search(query)
    if gcs_result.strip():
        return f"Google Search says: {gcs_result}"

    return ""
# utils/web_search.py
ddg_count = 0
gcs_count = 0

def get_ddg_count():
    return ddg_count

def get_gcs_count():
    return gcs_count

async def get_web_context(query: str) -> str:
    global ddg_count, gcs_count

    try:
        result = await run_ddg_search(query)
        if result:
            ddg_count += 1
            return result
    except Exception:
        pass

    # fallback to GCS
    try:
        result = await run_gcs_search(query)
        if result:
            gcs_count += 1
            return result
    except Exception:
        pass

    return ""


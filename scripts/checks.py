import httpx
import time
import json
import sys
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os

API_DOMAIN = os.getenv("API_DOMAIN", "").strip()
FALLBACK_API_DOMAIN = os.getenv("FALLBACK_API_DOMAIN", "").strip()
TIMEOUT = 5
CHECK_REGION = "gha"
HISTORY_DAYS = 90

# Paths relative to script location
SCRIPT_DIR = Path(__file__).parent
DOCS_DIR = SCRIPT_DIR.parent / "docs"
HISTORY_FILE = DOCS_DIR / "history.json"
OVERRIDE_FILE = DOCS_DIR / "override.json"
FEED_FILE = DOCS_DIR / "feed.xml"

if not API_DOMAIN:
    raise RuntimeError("API_DOMAIN environment variable is required")

ENDPOINTS = [
    {"name": "healthz", "url": f"https://{API_DOMAIN}/healthz", "critical": True},
    {"name": "readyz", "url": f"https://{API_DOMAIN}/readyz", "critical": True},
]

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.4 Safari/605.1.15"
    ),
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Cache-Control": "no-cache",
    "Pragma": "no-cache",
}


def check_endpoint(endpoint: Dict) -> Dict:
    name = endpoint["name"]
    url = endpoint["url"]
    
    start_time = time.time()
    result = {
        "name": name,
        "status": "fail",
        "latency_ms": None,
        "region": CHECK_REGION,
    }
    
    try:
        monitor_url = url + ("&" if "?" in url else "?") + "monitor=1"
        response = httpx.head(monitor_url, headers=DEFAULT_HEADERS, timeout=TIMEOUT, follow_redirects=True)
        if response.status_code in (405, 501):
            response = httpx.get(monitor_url, headers=DEFAULT_HEADERS, timeout=TIMEOUT, follow_redirects=True)
        latency_ms = int((time.time() - start_time) * 1000)
        result["latency_ms"] = latency_ms
        
        if 200 <= response.status_code < 300:
            result["status"] = "ok"
        else:
            if response.status_code in (403, 404):
                fallback_paths = [
                    monitor_url.replace("/healthz", "/health/"),
                    monitor_url.replace("/readyz", "/ready/"),
                ]
                for alt in fallback_paths:
                    if alt == monitor_url:
                        continue
                    try:
                        alt_start = time.time()
                        alt_resp = httpx.get(alt, headers=DEFAULT_HEADERS, timeout=TIMEOUT, follow_redirects=True)
                        result["latency_ms"] = int((time.time() - alt_start) * 1000)
                        if 200 <= alt_resp.status_code < 300:
                            result["status"] = "ok"
                            result.pop("error", None)
                            break
                    except (httpx.TimeoutException, httpx.ConnectError, httpx.RequestError):
                        continue
            if result["status"] != "ok" and FALLBACK_API_DOMAIN:
                try:
                    alt_url = monitor_url.replace(API_DOMAIN, FALLBACK_API_DOMAIN)
                    alt_start = time.time()
                    alt_resp = httpx.get(alt_url, headers=DEFAULT_HEADERS, timeout=TIMEOUT, follow_redirects=True)
                    result["latency_ms"] = int((time.time() - alt_start) * 1000)
                    if 200 <= alt_resp.status_code < 300:
                        result["status"] = "ok"
                        result.pop("error", None)
                except (httpx.TimeoutException, httpx.ConnectError, httpx.RequestError):
                    pass

            if result["status"] != "ok":
                result["status"] = "fail"
                result["error"] = f"HTTP {response.status_code}"
            
    except httpx.TimeoutException:
        result["error"] = "Timeout"
    except httpx.ConnectError:
        result["error"] = "Connection failed"
    except httpx.RequestError as e:
        result["error"] = f"Request error: {str(e)}"
    except (ValueError, TypeError, KeyError) as e:
        result["error"] = f"Data error: {str(e)}"
    except OSError as e:
        result["error"] = f"System error: {str(e)}"
    
    return result


def compute_overall_status(checks: List[Dict]) -> str:
    critical_failures = sum(
        1 for check in checks 
        if check.get("status") == "fail"
    )
    
    if critical_failures == 0:
        return "ok"
    elif critical_failures == 1:
        return "degraded"
    else:
        return "outage"


def load_history() -> Dict[str, Any]:
    """Load existing history or create empty structure."""
    if HISTORY_FILE.exists():
        try:
            with open(HISTORY_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    
    return {
        "checks": [],
        "daily_summary": {},
    }


def prune_old_data(history: Dict[str, Any]) -> Dict[str, Any]:
    """Remove data older than HISTORY_DAYS."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=HISTORY_DAYS)
    cutoff_str = cutoff.strftime('%Y-%m-%dT%H:%M:%SZ')
    cutoff_date = cutoff.strftime('%Y-%m-%d')
    
    # Prune checks
    history["checks"] = [
        c for c in history["checks"]
        if c.get("timestamp", "") >= cutoff_str
    ]
    
    # Prune daily_summary
    history["daily_summary"] = {
        date: stats for date, stats in history["daily_summary"].items()
        if date >= cutoff_date
    }
    
    return history


def update_history(history: Dict[str, Any], checks: List[Dict], timestamp: str) -> Dict[str, Any]:
    """Add new check results to history and update daily summary."""
    # Add to checks list
    check_entry: Dict[str, Any] = {"timestamp": timestamp}
    for check in checks:
        check_entry[check["name"]] = {
            "status": check["status"],
            "latency_ms": check.get("latency_ms"),
        }
    history["checks"].append(check_entry)
    
    # Update daily summary
    date = timestamp[:10]  # YYYY-MM-DD
    if date not in history["daily_summary"]:
        history["daily_summary"][date] = {}
    
    for check in checks:
        name = check["name"]
        if name not in history["daily_summary"][date]:
            history["daily_summary"][date][name] = {
                "up": 0,
                "down": 0,
                "total_latency_ms": 0,
                "check_count": 0,
            }
        
        stats = history["daily_summary"][date][name]
        if check["status"] == "ok":
            stats["up"] += 1
        else:
            stats["down"] += 1
        
        if check.get("latency_ms") is not None:
            stats["total_latency_ms"] += check["latency_ms"]
            stats["check_count"] += 1
    
    return history


def save_history(history: Dict[str, Any]) -> None:
    """Save history to file."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=2)


def load_override() -> Dict[str, Any]:
    """Load override.json for incidents and manual overrides."""
    if OVERRIDE_FILE.exists():
        try:
            with open(OVERRIDE_FILE, "r") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            pass
    return {"overall": None, "message": None, "incidents": []}


def generate_rss_feed(incidents: List[Dict], base_url: str = "https://status.joinevolve.app") -> str:
    """Generate RSS feed XML from incidents."""
    now = datetime.now(timezone.utc).strftime('%a, %d %b %Y %H:%M:%S +0000')
    
    items = []
    for incident in incidents[:20]:  # Last 20 incidents
        pub_date = datetime.fromisoformat(
            incident["created_at"].replace("Z", "+00:00")
        ).strftime('%a, %d %b %Y %H:%M:%S +0000')
        
        description = f"Status: {incident.get('status', 'unknown')}"
        if incident.get("updates"):
            latest = incident["updates"][-1]
            description += f"\n\nLatest update: {latest.get('message', '')}"
        
        items.append(f"""    <item>
      <title>{escape_xml(incident.get('title', 'Incident'))}</title>
      <description>{escape_xml(description)}</description>
      <pubDate>{pub_date}</pubDate>
      <guid>{base_url}/incidents/{incident.get('id', '')}</guid>
    </item>""")
    
    items_xml = "\n".join(items) if items else ""
    
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>Evolve Status</title>
    <link>{base_url}</link>
    <description>Status updates for Evolve services</description>
    <language>en-us</language>
    <lastBuildDate>{now}</lastBuildDate>
    <atom:link href="{base_url}/feed.xml" rel="self" type="application/rss+xml"/>
{items_xml}
  </channel>
</rss>
"""


def escape_xml(text: str) -> str:
    """Escape special XML characters."""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
        .replace("'", "&apos;")
    )


def save_rss_feed(incidents: List[Dict]) -> None:
    """Save RSS feed to file."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    feed_content = generate_rss_feed(incidents)
    with open(FEED_FILE, "w") as f:
        f.write(feed_content)


def generate_status() -> Dict:
    checks = []
    
    for endpoint in ENDPOINTS:
        check_result = check_endpoint(endpoint)
        checks.append(check_result)
    
    overall = compute_overall_status(checks)
    timestamp = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
    
    # Load and update history
    history = load_history()
    history = update_history(history, checks, timestamp)
    history = prune_old_data(history)
    save_history(history)
    
    # Load override data
    override = load_override()
    incidents = override.get("incidents", [])
    
    # Generate RSS feed
    save_rss_feed(incidents)
    
    status_doc = {
        "version": 1,
        "generated_at": timestamp,
        "ttl_seconds": 120,
        "overall": override.get("overall") or overall,
        "message": override.get("message") or "",
        "incidents": incidents,
        "checks": checks,
    }
    
    return status_doc


def main():
    try:
        status = generate_status()
        print(json.dumps(status, indent=2))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as e:
        error_status = {
            "version": 1,
            "generated_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "ttl_seconds": 120,
            "overall": "outage",
            "message": "Status check script error",
            "incidents": [],
            "checks": [
                {
                    "name": "script",
                    "status": "fail",
                    "latency_ms": None,
                    "region": CHECK_REGION,
                    "error": f"System error: {str(e)}",
                }
            ],
        }
        print(json.dumps(error_status, indent=2))
        return 1
    except Exception as e:
        error_status = {
            "version": 1,
            "generated_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
            "ttl_seconds": 120,
            "overall": "outage",
            "message": "Status check script error",
            "incidents": [],
            "checks": [
                {
                    "name": "script",
                    "status": "fail",
                    "latency_ms": None,
                    "region": CHECK_REGION,
                    "error": f"Unexpected error: {str(e)}",
                }
            ],
        }
        print(json.dumps(error_status, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())

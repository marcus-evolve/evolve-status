import httpx
import time
import json
import sys
from typing import Dict, List
import os

API_DOMAIN = os.getenv("API_DOMAIN", "").strip()
FALLBACK_API_DOMAIN = os.getenv("FALLBACK_API_DOMAIN", "").strip()
TIMEOUT = 5
CHECK_REGION = "gha"

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
                        # Fallback path failed, continue to next alternative
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
                    # Fallback domain failed, continue with original result
                    pass

            if result["status"] != "ok":
                result["status"] = "fail"
                result["error"] = f"HTTP {response.status_code}"
            
    except httpx.TimeoutException:
        result["error"] = "Timeout"
    except httpx.ConnectError:
        result["error"] = "Connection failed"
    except httpx.RequestError as e:
        # Catch any other httpx request-related errors
        result["error"] = f"Request error: {str(e)}"
    except (ValueError, TypeError, KeyError) as e:
        # Catch data processing errors
        result["error"] = f"Data error: {str(e)}"
    except OSError as e:
        # Catch system-level errors (e.g., from time.time())
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


def generate_status() -> Dict:
    checks = []
    
    for endpoint in ENDPOINTS:
        check_result = check_endpoint(endpoint)
        checks.append(check_result)
    
    overall = compute_overall_status(checks)
    
    status_doc = {
        "version": 1,
        "generated_at": time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime()),
        "ttl_seconds": 120,
        "overall": overall,
        "message": "",
        "incidents": [],
        "checks": checks,
    }
    
    return status_doc


def main():
    try:
        status = generate_status()
        print(json.dumps(status, indent=2))
        return 0
    except (ValueError, TypeError, KeyError, OSError) as e:
        # Catch expected errors from data processing or system operations
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
        # Catch any truly unexpected errors (should be rare)
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


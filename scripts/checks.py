#!/usr/bin/env python3
"""
Health check script for Evolve status monitoring.

Performs synthetic checks against the backend API and generates status.json.
Runs in GitHub Actions every 2 minutes.

Exit codes:
  0: Success (status generated)
  1: Script error (but may still output partial status)
"""

import httpx
import time
import json
import sys
from typing import Dict, List, Optional


# Configuration
API_DOMAIN = "production.joinevolve.app"  # Replace with your Railway domain
TIMEOUT = 5  # seconds
CHECK_REGION = "gha"  # GitHub Actions

ENDPOINTS = [
    {"name": "healthz", "url": f"https://{API_DOMAIN}/healthz", "critical": True},
    {"name": "readyz", "url": f"https://{API_DOMAIN}/readyz", "critical": True},
]


def check_endpoint(endpoint: Dict) -> Dict:
    """
    Check a single endpoint and return result.
    
    Returns:
        {
            "name": str,
            "status": "ok" | "fail",
            "latency_ms": int | None,
            "region": str,
            "error": str (optional)
        }
    """
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
        response = httpx.get(url, timeout=TIMEOUT, follow_redirects=True)
        latency_ms = int((time.time() - start_time) * 1000)
        result["latency_ms"] = latency_ms
        
        # Consider 2xx status codes as success
        if 200 <= response.status_code < 300:
            result["status"] = "ok"
        else:
            result["status"] = "fail"
            result["error"] = f"HTTP {response.status_code}"
            
    except httpx.TimeoutException:
        result["error"] = "Timeout"
    except httpx.ConnectError:
        result["error"] = "Connection failed"
    except Exception as e:
        result["error"] = str(e)
    
    return result


def compute_overall_status(checks: List[Dict]) -> str:
    """
    Compute overall status based on check results.
    
    Logic:
    - ok: All checks pass
    - degraded: 1 critical check fails
    - outage: 2+ critical checks fail
    
    Returns:
        "ok" | "degraded" | "outage"
    """
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
    """
    Run all checks and generate status document.
    
    Returns:
        Status document dict matching schema
    """
    checks = []
    
    # Run all endpoint checks
    for endpoint in ENDPOINTS:
        check_result = check_endpoint(endpoint)
        checks.append(check_result)
    
    # Compute overall status
    overall = compute_overall_status(checks)
    
    # Generate status document
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
    """Main entry point."""
    try:
        status = generate_status()
        print(json.dumps(status, indent=2))
        return 0
    except Exception as e:
        # Even on error, output a fail-safe status
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
                    "error": str(e),
                }
            ],
        }
        print(json.dumps(error_status, indent=2))
        return 1


if __name__ == "__main__":
    sys.exit(main())


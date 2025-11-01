# Evolve Status

This repository hosts the status page infrastructure for Evolve, providing real-time health monitoring and outage notifications for the iOS app.

## Overview

- **GitHub Pages**: Serves `docs/status.json` publicly at `https://marcus-evolve.github.io/evolve-status/status.json`
- **GitHub Actions**: Runs health checks every 2 minutes and updates status
- **Manual Override**: Edit `docs/override.json` during incidents to force status/message

## Setup

1. **Enable GitHub Pages**:
   - Go to repository Settings → Pages
   - Source: Deploy from a branch
   - Branch: `main`, folder: `/docs`
   - Save

2. **Configure API Domain**:
   - Edit `scripts/checks.py` and replace the placeholder with your actual Railway domain
   - Example: `evolve-backend-production.up.railway.app`
   - You can find this in your Railway project dashboard

3. **Test Workflow**:
   - Go to Actions tab
   - Run "Publish status" workflow manually
   - Verify `docs/status.json` is updated

## Usage

### Normal Operations

The GitHub Action runs automatically every 2 minutes, checking:
- `/healthz` - Basic service health
- `/readyz` - Database, cache, and dependencies

Status is computed based on:
- `ok`: All checks pass
- `degraded`: 1 check fails
- `outage`: 2+ checks fail

### Manual Override (Incidents)

When you detect an incident:

1. Edit `docs/override.json`:
```json
{
  "overall": "outage",
  "message": "We're experiencing elevated error rates. Our team is investigating.",
  "incidents": [
    {
      "id": "2025-11-01-railway",
      "status": "identified",
      "severity": "major",
      "title": "Elevated API errors",
      "updated_at": "2025-11-01T12:00:00Z"
    }
  ]
}
```

2. Commit and push
3. Go to Actions → "Publish status" → Run workflow (to publish immediately)

### Recovery

When resolved:

1. Clear `docs/override.json`:
```json
{
  "overall": null,
  "message": null,
  "incidents": []
}
```

2. Commit, push, and trigger workflow

## Status Schema

```json
{
  "version": 1,
  "generated_at": "ISO-8601 timestamp",
  "ttl_seconds": 120,
  "overall": "ok | degraded | outage",
  "message": "Optional user-facing message",
  "incidents": [
    {
      "id": "unique-incident-id",
      "status": "identified | monitoring | resolved",
      "severity": "minor | major | critical",
      "title": "Brief description",
      "updated_at": "ISO-8601 timestamp"
    }
  ],
  "checks": [
    {
      "name": "healthz",
      "status": "ok | fail",
      "latency_ms": 123,
      "region": "gha"
    }
  ]
}
```

## Monitoring

- Status URL: `https://marcus-evolve.github.io/evolve-status/status.json`
- iOS app polls this URL on launch, foreground, and retry
- Cache-Control: `max-age=60` (CDN cache)
- TTL: 120 seconds (client-side freshness)

## Troubleshooting

- **Checks failing**: Verify API domain in `scripts/checks.py`
- **Pages not updating**: Check Actions tab for workflow errors
- **404 on status.json**: Ensure GitHub Pages is enabled and deployed from `/docs`


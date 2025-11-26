import { Incident } from '../types'
import './IncidentHistory.css'

interface IncidentHistoryProps {
  incidents: Incident[]
}

function formatDate(isoString: string): string {
  const date = new Date(isoString)
  return date.toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  })
}

function formatTime(isoString: string): string {
  const date = new Date(isoString)
  return date.toLocaleTimeString(undefined, {
    hour: '2-digit',
    minute: '2-digit',
  })
}

const IMPACT_LABELS: Record<string, string> = {
  none: 'Maintenance',
  minor: 'Minor',
  major: 'Major',
  critical: 'Critical',
}

const STATUS_LABELS: Record<string, string> = {
  investigating: 'Investigating',
  identified: 'Identified',
  monitoring: 'Monitoring',
  resolved: 'Resolved',
}

function IncidentHistory({ incidents }: IncidentHistoryProps) {
  if (!incidents || incidents.length === 0) {
    return (
      <div className="incident-history">
        <h2 className="incident-history-title">Recent Notices</h2>
        <div className="incident-empty">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <circle cx="12" cy="12" r="10" />
            <path d="M8 12l3 3 5-5" />
          </svg>
          <p>No incidents reported in the past 90 days</p>
        </div>
      </div>
    )
  }

  // Sort by date, most recent first
  const sortedIncidents = [...incidents].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  )

  return (
    <div className="incident-history">
      <h2 className="incident-history-title">Recent Notices</h2>
      <div className="incident-list">
        {sortedIncidents.map((incident) => (
          <article key={incident.id} className={`incident incident--${incident.impact}`}>
            <header className="incident-header">
              <div className="incident-meta">
                <span className={`incident-impact incident-impact--${incident.impact}`}>
                  {IMPACT_LABELS[incident.impact] || incident.impact}
                </span>
                <span className={`incident-status incident-status--${incident.status}`}>
                  {STATUS_LABELS[incident.status] || incident.status}
                </span>
              </div>
              <time className="incident-date" dateTime={incident.created_at}>
                {formatDate(incident.created_at)}
              </time>
            </header>
            
            <h3 className="incident-title">{incident.title}</h3>
            
            {incident.updates && incident.updates.length > 0 && (
              <div className="incident-updates">
                {incident.updates.map((update, i) => (
                  <div key={i} className="incident-update">
                    <time className="incident-update-time" dateTime={update.timestamp}>
                      {formatTime(update.timestamp)}
                    </time>
                    {update.status && (
                      <span className={`incident-update-status incident-status--${update.status}`}>
                        {STATUS_LABELS[update.status] || update.status}
                      </span>
                    )}
                    <p className="incident-update-message">{update.message}</p>
                  </div>
                ))}
              </div>
            )}
            
            {incident.affected_components && incident.affected_components.length > 0 && (
              <div className="incident-affected">
                <span className="incident-affected-label">Affected:</span>
                {incident.affected_components.join(', ')}
              </div>
            )}
          </article>
        ))}
      </div>
    </div>
  )
}

export default IncidentHistory

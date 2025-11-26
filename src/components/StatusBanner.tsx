import { OverallStatus } from '../types'
import './StatusBanner.css'

interface StatusBannerProps {
  overall: OverallStatus
  message?: string
}

const STATUS_CONFIG = {
  ok: {
    label: 'All systems operational',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="status-icon status-icon--ok">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
        <path d="M8 12l3 3 5-5" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    ),
  },
  degraded: {
    label: 'Partial system outage',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="status-icon status-icon--degraded">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
        <path d="M12 8v4M12 16h.01" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    ),
  },
  outage: {
    label: 'Major system outage',
    icon: (
      <svg viewBox="0 0 24 24" fill="none" className="status-icon status-icon--outage">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="2" />
        <path d="M15 9l-6 6M9 9l6 6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" />
      </svg>
    ),
  },
}

function StatusBanner({ overall, message }: StatusBannerProps) {
  const config = STATUS_CONFIG[overall] || STATUS_CONFIG.ok

  return (
    <div className={`status-banner status-banner--${overall}`}>
      {config.icon}
      <div className="status-banner-content">
        <h1 className="status-banner-title">{config.label}</h1>
        {message && <p className="status-banner-message">{message}</p>}
      </div>
    </div>
  )
}

export default StatusBanner

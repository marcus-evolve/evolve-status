import { useState } from 'react'
import { CheckResult, HistoryData } from '../types'
import UptimeGraph from './UptimeGraph'
import './ComponentRow.css'

interface ComponentRowProps {
  check: CheckResult
  history: HistoryData | null
}

const DISPLAY_NAMES: Record<string, string> = {
  healthz: 'API Health',
  readyz: 'API Readiness',
}

function ComponentRow({ check, history }: ComponentRowProps) {
  const [expanded, setExpanded] = useState(false)
  
  const displayName = DISPLAY_NAMES[check.name] || check.name
  const statusClass = check.status === 'ok' ? 'ok' : check.status === 'degraded' ? 'degraded' : 'outage'

  return (
    <div className={`component-row ${expanded ? 'component-row--expanded' : ''}`}>
      <button
        className="component-row-header"
        onClick={() => setExpanded(!expanded)}
        aria-expanded={expanded}
      >
        <div className="component-row-left">
          <span className={`component-status-dot component-status-dot--${statusClass}`} aria-hidden="true" />
          <span className="component-name">{displayName}</span>
        </div>
        
        <div className="component-row-right">
          {check.latency_ms !== null && (
            <span className="component-latency">~{check.latency_ms} ms</span>
          )}
          <svg 
            className={`component-chevron ${expanded ? 'component-chevron--expanded' : ''}`}
            width="16" 
            height="16" 
            viewBox="0 0 24 24" 
            fill="none" 
            stroke="currentColor" 
            strokeWidth="2"
          >
            <path d="M6 9l6 6 6-6" />
          </svg>
        </div>
      </button>
      
      {expanded && (
        <div className="component-row-details">
          <UptimeGraph checkName={check.name} history={history} />
          {check.error && (
            <div className="component-error">
              <span className="component-error-label">Error:</span>
              <span className="component-error-message">{check.error}</span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

export default ComponentRow

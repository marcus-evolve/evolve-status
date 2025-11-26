export type ServiceStatus = 'ok' | 'degraded' | 'fail'
export type OverallStatus = 'ok' | 'degraded' | 'outage'
export type IncidentStatus = 'investigating' | 'identified' | 'monitoring' | 'resolved'
export type IncidentImpact = 'none' | 'minor' | 'major' | 'critical'

export interface CheckResult {
  name: string
  status: ServiceStatus
  latency_ms: number | null
  region: string
  error?: string
}

export interface StatusData {
  version: number
  generated_at: string
  ttl_seconds: number
  overall: OverallStatus
  message: string
  incidents: Incident[]
  checks: CheckResult[]
}

export interface IncidentUpdate {
  timestamp: string
  message: string
  status?: IncidentStatus
}

export interface Incident {
  id: string
  title: string
  status: IncidentStatus
  impact: IncidentImpact
  created_at: string
  resolved_at?: string
  updates: IncidentUpdate[]
  affected_components?: string[]
}

export interface DailyCheckStats {
  up: number
  down: number
  total_latency_ms: number
  check_count: number
}

export interface DailySummary {
  [date: string]: {
    [checkName: string]: DailyCheckStats
  }
}

export interface HistoricalCheck {
  timestamp: string
  [checkName: string]: { status: ServiceStatus; latency_ms: number | null } | string
}

export interface HistoryData {
  checks: HistoricalCheck[]
  daily_summary: DailySummary
}

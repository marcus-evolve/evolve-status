import { useMemo } from 'react'
import { HistoryData, DailyCheckStats } from '../types'
import './UptimeGraph.css'

interface UptimeGraphProps {
  checkName: string
  history: HistoryData | null
  days?: number
}

interface DayData {
  date: string
  uptime: number | null
  status: 'ok' | 'degraded' | 'outage' | 'unknown'
}

function UptimeGraph({ checkName, history, days = 60 }: UptimeGraphProps) {
  const dayData = useMemo((): DayData[] => {
    const result: DayData[] = []
    const today = new Date()
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - i)
      const dateStr = date.toISOString().split('T')[0]
      
      const stats = history?.daily_summary?.[dateStr]?.[checkName] as DailyCheckStats | undefined
      
      if (stats && (stats.up + stats.down) > 0) {
        const total = stats.up + stats.down
        const uptime = (stats.up / total) * 100
        
        let status: DayData['status'] = 'ok'
        if (uptime < 99) status = 'degraded'
        if (uptime < 95) status = 'outage'
        
        result.push({ date: dateStr, uptime, status })
      } else {
        result.push({ date: dateStr, uptime: null, status: 'unknown' })
      }
    }
    
    return result
  }, [checkName, history, days])

  const uptimePercent = useMemo(() => {
    const daysWithData = dayData.filter(d => d.uptime !== null)
    if (daysWithData.length === 0) return null
    
    const avgUptime = daysWithData.reduce((sum, d) => sum + (d.uptime || 0), 0) / daysWithData.length
    return avgUptime
  }, [dayData])

  return (
    <div className="uptime-graph">
      <div className="uptime-graph-header">
        <span className="uptime-graph-range">{days} days ago</span>
        {uptimePercent !== null && (
          <span className={`uptime-percent uptime-percent--${uptimePercent >= 99.5 ? 'ok' : uptimePercent >= 95 ? 'degraded' : 'outage'}`}>
            {uptimePercent.toFixed(2)}% uptime
          </span>
        )}
        <span className="uptime-graph-range">Today</span>
      </div>
      
      <div className="uptime-bars" role="img" aria-label={`Uptime history for ${checkName}`}>
        {dayData.map((day, i) => (
          <div
            key={day.date}
            className={`uptime-bar uptime-bar--${day.status}`}
            title={day.uptime !== null ? `${day.date}: ${day.uptime.toFixed(1)}% uptime` : `${day.date}: No data`}
            style={{ animationDelay: `${i * 8}ms` }}
          />
        ))}
      </div>
    </div>
  )
}

export default UptimeGraph

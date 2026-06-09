import React from 'react'
import clsx from 'clsx'

export function StatusBadge({ status }) {
  const statusConfig = {
    Draft: { bg: 'bg-slate-100', text: 'text-slate-800', icon: '●' },
    Analyzing: { bg: 'bg-blue-100', text: 'text-blue-800', icon: '◐' },
    'Needs Review': { bg: 'bg-amber-100', text: 'text-amber-800', icon: '⚠' },
    Finalized: { bg: 'bg-emerald-100', text: 'text-emerald-800', icon: '✓' },
  }
  
  const config = statusConfig[status] || statusConfig.Draft
  
  return (
    <span className={clsx('inline-flex items-center gap-2 px-3 py-1 rounded-full text-sm font-medium', config.bg, config.text)}>
      <span>{config.icon}</span>
      {status}
    </span>
  )
}

export function HealthBadge({ health }) {
  const healthConfig = {
    healthy: { bg: 'bg-emerald-100', text: 'text-emerald-800', label: '✓ Healthy' },
    fragile: { bg: 'bg-amber-100', text: 'text-amber-800', label: '⚠ Fragile' },
    distortionary: { bg: 'bg-red-100', text: 'text-red-800', label: '✗ Distortionary' },
    misleading: { bg: 'bg-red-100', text: 'text-red-800', label: '✗ Misleading' },
  }
  
  const config = healthConfig[health] || { bg: 'bg-slate-100', text: 'text-slate-800', label: 'Unknown' }
  
  return (
    <span className={clsx('inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium', config.bg, config.text)}>
      {config.label}
    </span>
  )
}

export function SeverityBadge({ severity }) {
  const severityConfig = {
    low: { bg: 'bg-emerald-100', text: 'text-emerald-800' },
    medium: { bg: 'bg-amber-100', text: 'text-amber-800' },
    high: { bg: 'bg-orange-100', text: 'text-orange-800' },
    critical: { bg: 'bg-red-100', text: 'text-red-800' },
    none: { bg: 'bg-slate-100', text: 'text-slate-800' },
    'at_risk': { bg: 'bg-amber-100', text: 'text-amber-800' },
    unsustainable: { bg: 'bg-red-100', text: 'text-red-800' },
    sustainable: { bg: 'bg-emerald-100', text: 'text-emerald-800' },
  }
  
  const config = severityConfig[severity] || severityConfig.low
  
  return (
    <span className={clsx('inline-flex items-center px-3 py-1 rounded-full text-sm font-medium', config.bg, config.text)}>
      {severity.replace(/_/g, ' ')}
    </span>
  )
}

export function ConfidenceBar({ confidence }) {
  const percentage = (confidence * 100).toFixed(0)
  const getColor = (conf) => {
    if (conf >= 0.9) return 'bg-emerald-500'
    if (conf >= 0.75) return 'bg-blue-500'
    if (conf >= 0.6) return 'bg-amber-500'
    return 'bg-red-500'
  }
  
  return (
    <div className="flex items-center gap-2">
      <div className="flex-1 bg-slate-200 rounded-full h-2">
        <div
          className={clsx('h-2 rounded-full transition-all', getColor(confidence))}
          style={{ width: `${percentage}%` }}
        />
      </div>
      <span className="text-sm font-medium text-slate-700 min-w-12">{percentage}%</span>
    </div>
  )
}

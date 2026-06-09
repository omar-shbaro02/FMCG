import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { Plus, RefreshCw } from 'lucide-react'
import { caseAPI } from '../hooks/useAPI'
import { StatusBadge, HealthBadge, ConfidenceBar } from '../components/Badges'

export default function Dashboard() {
  const [cases, setCases] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    loadCases()
    // Refresh every 5 seconds
    const interval = setInterval(loadCases, 5000)
    return () => clearInterval(interval)
  }, [])

  const loadCases = async () => {
    try {
      const data = await caseAPI.getCases()
      setCases(data.cases)
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-slate-900" />
          <p className="mt-4 text-slate-600">Loading cases...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-slate-900">Dashboard</h1>
          <p className="text-slate-600 mt-2">Trade Promotion Analysis Cases</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={loadCases}
            className="btn btn-secondary flex items-center gap-2"
          >
            <RefreshCw size={16} />
            Refresh
          </button>
          <Link to="/cases/new" className="btn btn-primary flex items-center gap-2">
            <Plus size={16} />
            New Case
          </Link>
        </div>
      </div>

      {/* Summary Stats */}
      <div className="grid grid-cols-4 gap-4">
        <div className="card p-4">
          <div className="text-sm font-medium text-slate-600">Total Cases</div>
          <div className="text-3xl font-bold text-slate-900 mt-2">{cases.length}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm font-medium text-slate-600">Draft</div>
          <div className="text-3xl font-bold text-slate-500 mt-2">
            {cases.filter(c => c.status === 'Draft').length}
          </div>
        </div>
        <div className="card p-4">
          <div className="text-sm font-medium text-slate-600">Needs Review</div>
          <div className="text-3xl font-bold text-amber-600 mt-2">
            {cases.filter(c => c.status === 'Needs Review').length}
          </div>
        </div>
        <div className="card p-4">
          <div className="text-sm font-medium text-slate-600">Finalized</div>
          <div className="text-3xl font-bold text-emerald-600 mt-2">
            {cases.filter(c => c.status === 'Finalized').length}
          </div>
        </div>
      </div>

      {/* Cases Table */}
      <div className="card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-slate-100 border-b border-slate-200">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Promotion ID</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Brand / Category</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Status</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Growth Health</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Distortion</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Confidence</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Recommended Action</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-slate-900">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {cases.map((c) => (
                <tr key={c.id} className="hover:bg-slate-50 transition">
                  <td className="px-6 py-4 text-sm font-medium text-slate-900">
                    {c.promotion_id}
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-700">
                    <div>{c.brand}</div>
                    <div className="text-slate-600">{c.category}</div>
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <StatusBadge status={c.status} />
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {c.growth_health ? <HealthBadge health={c.growth_health} /> : '—'}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {c.distortion_severity ? (
                      <span className="text-slate-700">{c.distortion_severity}</span>
                    ) : (
                      '—'
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    {c.confidence ? <ConfidenceBar confidence={c.confidence} /> : '—'}
                  </td>
                  <td className="px-6 py-4 text-sm text-slate-700 max-w-xs truncate">
                    {c.recommended_action || '—'}
                  </td>
                  <td className="px-6 py-4 text-sm">
                    <Link to={`/cases/${c.id}`} className="text-blue-600 hover:text-blue-800 font-medium">
                      View
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        {cases.length === 0 && (
          <div className="text-center py-12">
            <p className="text-slate-600">No cases yet. Create one to get started.</p>
          </div>
        )}
      </div>

      {error && (
        <div className="card bg-red-50 border-red-200 p-4 text-red-800">
          Error: {error}
        </div>
      )}
    </div>
  )
}

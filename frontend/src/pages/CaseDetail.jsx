import React, { useState, useEffect } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { caseAPI } from '../hooks/useAPI'
import { AlertCircle, CheckCircle, Clock, ChevronDown, ChevronUp } from 'lucide-react'
import { StatusBadge, HealthBadge, SeverityBadge, ConfidenceBar } from '../components/Badges'

export default function CaseDetail() {
  const { caseId } = useParams()
  const navigate = useNavigate()
  const [caseData, setCaseData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [analyzing, setAnalyzing] = useState(false)
  const [error, setError] = useState(null)
  const [activeTab, setActiveTab] = useState('data')
  const [expandedAgents, setExpandedAgents] = useState({})
  const [humanNotes, setHumanNotes] = useState('')

  useEffect(() => {
    loadCase()
    // Poll for updates every 3 seconds if still analyzing
    const interval = setInterval(loadCase, 3000)
    return () => clearInterval(interval)
  }, [caseId])

  const loadCase = async () => {
    try {
      const data = await caseAPI.getCase(caseId)
      setCaseData(data)
      setAnalyzing(data.case.status === 'Analyzing')
      setError(null)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const handleStartAnalysis = async () => {
    try {
      setAnalyzing(true)
      await caseAPI.analyzeCase(caseId)
      loadCase()
    } catch (err) {
      setError(err.message)
      setAnalyzing(false)
    }
  }

  const handleApprove = async () => {
    try {
      await caseAPI.approveCase(caseId, humanNotes)
      loadCase()
      setActiveTab('judgment')
    } catch (err) {
      setError(err.message)
    }
  }

  const handleRequestReanalysis = async () => {
    try {
      await caseAPI.requestReanalysis(caseId, humanNotes || 'User requested re-analysis')
      await caseAPI.analyzeCase(caseId)
      loadCase()
      setActiveTab('workflow')
    } catch (err) {
      setError(err.message)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-slate-900" />
          <p className="mt-4 text-slate-600">Loading case...</p>
        </div>
      </div>
    )
  }

  if (!caseData) {
    return (
      <div className="card bg-red-50 border-red-200 p-6 text-center">
        <AlertCircle className="inline-block text-red-600 mb-2" size={32} />
        <p className="text-red-800 font-medium">Case not found</p>
        <button onClick={() => navigate('/')} className="btn btn-secondary mt-4">
          Back to Dashboard
        </button>
      </div>
    )
  }

  const c = caseData.case
  const agents = caseData.agent_outputs

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-slate-900">{c.promotion_id}</h1>
          <p className="text-slate-600 mt-2">
            {c.brand} | {c.category} | {c.channel}
          </p>
        </div>
        <div className="text-right">
          <StatusBadge status={c.status} />
          {agents.agent_6 && <HealthBadge health={agents.agent_6.growth_health} />}
        </div>
      </div>

      {error && (
        <div className="card bg-red-50 border-red-200 p-4 flex gap-3">
          <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
          <div className="text-red-800">{error}</div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-slate-200 flex gap-8">
        {[
          { id: 'data', label: 'Case Data' },
          { id: 'workflow', label: 'Agent Analysis', badge: analyzing ? '⏳' : Object.keys(agents).length },
          { id: 'judgment', label: 'Final Judgment', badge: agents.agent_6 ? '✓' : null },
          { id: 'review', label: 'Human Review', badge: c.human_review_approved ? '✓' : null },
        ].map(tab => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`pb-3 px-1 border-b-2 transition font-medium ${
              activeTab === tab.id
                ? 'border-slate-900 text-slate-900'
                : 'border-transparent text-slate-600 hover:text-slate-900'
            }`}
          >
            {tab.label}
            {tab.badge && (
              <span className="ml-2 text-sm bg-slate-900 text-white rounded-full px-2 py-0 inline-block">
                {tab.badge}
              </span>
            )}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'data' && <TabCaseData caseData={c} />}

      {activeTab === 'workflow' && (
        <TabWorkflow
          caseData={c}
          agents={agents}
          analyzing={analyzing}
          expandedAgents={expandedAgents}
          setExpandedAgents={setExpandedAgents}
          onStartAnalysis={handleStartAnalysis}
        />
      )}

      {activeTab === 'judgment' && agents.agent_6 && (
        <TabJudgment agents={agents} />
      )}

      {activeTab === 'review' && (
        <TabHumanReview
          caseData={c}
          humanNotes={humanNotes}
          setHumanNotes={setHumanNotes}
          onApprove={handleApprove}
          onReanalyze={handleRequestReanalysis}
          agents={agents}
        />
      )}

      {/* Footer Actions */}
      <div className="flex gap-4 justify-between py-4 border-t border-slate-200">
        <button onClick={() => navigate('/')} className="btn btn-secondary">
          Back to Dashboard
        </button>
        {c.status === 'Draft' && !analyzing && (
          <button onClick={handleStartAnalysis} className="btn btn-primary">
            Start Analysis
          </button>
        )}
      </div>
    </div>
  )
}

function TabCaseData({ caseData }) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div className="card p-4">
          <div className="text-sm text-slate-600 font-medium">Brand</div>
          <div className="text-lg font-bold text-slate-900">{caseData.brand}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-slate-600 font-medium">Category</div>
          <div className="text-lg font-bold text-slate-900">{caseData.category}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-slate-600 font-medium">SKU</div>
          <div className="text-lg font-bold text-slate-900">{caseData.sku}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-slate-600 font-medium">Channel</div>
          <div className="text-lg font-bold text-slate-900">{caseData.channel}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-slate-600 font-medium">Region</div>
          <div className="text-lg font-bold text-slate-900">{caseData.region}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-slate-600 font-medium">Key Account</div>
          <div className="text-lg font-bold text-slate-900">{caseData.key_account || '—'}</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-4 mt-6">
        <div className="card p-4">
          <div className="text-sm text-slate-600 font-medium">Promotion Type</div>
          <div className="text-lg font-bold text-slate-900">{caseData.promotion_type}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-slate-600 font-medium">Campaign Objective</div>
          <div className="text-lg font-bold text-slate-900">{caseData.campaign_objective}</div>
        </div>
        <div className="card p-4">
          <div className="text-sm text-slate-600 font-medium">Period</div>
          <div className="text-sm font-bold text-slate-900">
            {caseData.promotion_period_start} to {caseData.promotion_period_end}
          </div>
        </div>
      </div>

      <div className="card p-6">
        <h3 className="font-bold text-slate-900 mb-4">Sales Metrics</h3>
        <div className="grid grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-slate-600">Baseline Volume</div>
            <div className="text-2xl font-bold text-slate-900">{caseData.baseline_sales_volume.toLocaleString()}</div>
            <div className="text-xs text-slate-500">units</div>
          </div>
          <div>
            <div className="text-sm text-slate-600">Promo Volume</div>
            <div className="text-2xl font-bold text-slate-900">{caseData.promotion_sales_volume.toLocaleString()}</div>
            <div className="text-xs text-slate-500">units</div>
          </div>
          <div>
            <div className="text-sm text-slate-600">Uplift</div>
            <div className="text-2xl font-bold text-emerald-600">+{caseData.uplift_percent.toFixed(1)}%</div>
            <div className="text-xs text-slate-500">percentage</div>
          </div>
          <div>
            <div className="text-sm text-slate-600">Confidence</div>
            <div className="text-2xl font-bold text-slate-900">{caseData.data_quality_confidence}</div>
            <div className="text-xs text-slate-500">% quality</div>
          </div>
        </div>
      </div>

      <div className="card p-6">
        <h3 className="font-bold text-slate-900 mb-4">Concentration Metrics</h3>
        <div className="grid grid-cols-3 gap-4">
          <div>
            <div className="text-sm text-slate-600 mb-2">Key Account Contribution</div>
            <div className="text-3xl font-bold text-slate-900">{caseData.key_account_contribution_percent.toFixed(1)}%</div>
          </div>
          <div>
            <div className="text-sm text-slate-600 mb-2">Channel Contribution</div>
            <div className="text-3xl font-bold text-slate-900">{caseData.channel_contribution_percent.toFixed(1)}%</div>
          </div>
          <div>
            <div className="text-sm text-slate-600 mb-2">Customers/Stores</div>
            <div className="text-3xl font-bold text-slate-900">{caseData.num_participating_customers}</div>
          </div>
        </div>
      </div>

      <div className="card p-6">
        <h3 className="font-bold text-slate-900 mb-4">Financial Impact</h3>
        <div className="grid grid-cols-4 gap-4">
          <div>
            <div className="text-sm text-slate-600">Discount</div>
            <div className="text-3xl font-bold text-slate-900">{caseData.discount_percent.toFixed(1)}%</div>
          </div>
          <div>
            <div className="text-sm text-slate-600">Trade Spend</div>
            <div className="text-3xl font-bold text-slate-900">${caseData.trade_spend.toLocaleString()}</div>
          </div>
          <div>
            <div className="text-sm text-slate-600">Margin Before</div>
            <div className="text-3xl font-bold text-slate-900">{caseData.gross_margin_before.toFixed(1)}%</div>
          </div>
          <div>
            <div className="text-sm text-slate-600">Margin During</div>
            <div className="text-3xl font-bold text-slate-900">{caseData.gross_margin_during.toFixed(1)}%</div>
          </div>
        </div>
      </div>

      {caseData.management_notes && (
        <div className="card p-6 bg-blue-50 border-blue-200">
          <h3 className="font-bold text-slate-900 mb-2">Management Notes</h3>
          <p className="text-slate-700">{caseData.management_notes}</p>
        </div>
      )}
    </div>
  )
}

function TabWorkflow({ caseData, agents, analyzing, expandedAgents, setExpandedAgents, onStartAnalysis }) {
  const agentList = [
    { num: 1, name: 'Campaign Intent & Commercial Context Analyst', key: 'agent_1' },
    { num: 2, name: 'Trade Concentration & Key Account Risk Analyst', key: 'agent_2' },
    { num: 3, name: 'Margin & Trade Efficiency Analyst', key: 'agent_3' },
    { num: 4, name: 'Demand & Inventory Propagation Analyst', key: 'agent_4' },
    { num: 5, name: 'Governance & Escalation Analyst', key: 'agent_5' },
    { num: 6, name: 'Executive Distortion Intelligence Brain', key: 'agent_6' },
  ]

  return (
    <div className="space-y-4">
      <div className="card p-4 bg-blue-50 border-blue-200">
        <p className="text-blue-800">
          {analyzing
            ? '🔄 Analysis in progress. The system is evaluating this promotion across all 6 specialist agents.'
            : Object.keys(agents).length === 0
              ? '⏳ Analysis not started. Click "Start Analysis" to begin.'
              : '✓ Analysis complete. Review agent outputs below.'}
        </p>
      </div>

      {Object.keys(agents).length === 0 && !analyzing && (
        <button onClick={onStartAnalysis} className="btn btn-primary w-full py-3 text-lg">
          Start Agent Analysis Workflow
        </button>
      )}

      {/* Stepper */}
      <div className="space-y-3">
        {agentList.map((agent, idx) => (
          <div key={agent.key}>
            <button
              onClick={() =>
                setExpandedAgents(prev => ({
                  ...prev,
                  [agent.key]: !prev[agent.key],
                }))
              }
              className="w-full card p-4 hover:bg-slate-50 transition flex items-center justify-between"
            >
              <div className="flex items-center gap-4 flex-1 text-left">
                <div
                  className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center font-bold text-white ${
                    agents[agent.key]
                      ? 'bg-emerald-500'
                      : analyzing && idx === Object.keys(agents).length
                        ? 'bg-blue-500 animate-pulse'
                        : 'bg-slate-300'
                  }`}
                >
                  {agents[agent.key] ? '✓' : agent.num}
                </div>
                <div>
                  <div className="font-medium text-slate-900">Agent {agent.num}: {agent.name}</div>
                  {agents[agent.key] && (
                    <div className="text-sm text-emerald-600 flex items-center gap-2 mt-1">
                      <ConfidenceBar confidence={agents[agent.key].confidence} />
                    </div>
                  )}
                </div>
              </div>
              {expandedAgents[agent.key] ? (
                <ChevronUp size={20} className="text-slate-600" />
              ) : (
                <ChevronDown size={20} className="text-slate-600" />
              )}
            </button>

            {/* Expanded Content */}
            {expandedAgents[agent.key] && agents[agent.key] && (
              <div className="card p-6 bg-slate-50 border-l-4 border-emerald-500 ml-6 mt-2">
                <AgentOutput agent={agent} output={agents[agent.key]} />
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

function AgentOutput({ agent, output }) {
  const renderValue = (value) => {
    if (typeof value === 'object') {
      return <pre className="text-xs bg-white p-2 rounded overflow-auto">{JSON.stringify(value, null, 2)}</pre>
    }
    return <span>{String(value)}</span>
  }

  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        {Object.entries(output)
          .filter(([key]) => key !== 'confidence')
          .slice(0, 6)
          .map(([key, value]) => (
            <div key={key}>
              <div className="text-sm font-medium text-slate-600 mb-1">{key.replace(/_/g, ' ')}</div>
              <div className="text-sm text-slate-900">{renderValue(value)}</div>
            </div>
          ))}
      </div>
      {Object.keys(output).length > 6 && (
        <details className="text-sm">
          <summary className="cursor-pointer text-slate-600 hover:text-slate-900">Show more fields...</summary>
          <div className="grid grid-cols-2 gap-4 mt-3">
            {Object.entries(output)
              .filter(([key]) => key !== 'confidence')
              .slice(6)
              .map(([key, value]) => (
                <div key={key}>
                  <div className="text-sm font-medium text-slate-600 mb-1">{key.replace(/_/g, ' ')}</div>
                  <div className="text-sm text-slate-900">{renderValue(value)}</div>
                </div>
              ))}
          </div>
        </details>
      )}
    </div>
  )
}

function TabJudgment({ agents }) {
  const judgment = agents.agent_6
  if (!judgment) return null

  return (
    <div className="space-y-6">
      {/* Executive Summary */}
      <div className="grid grid-cols-2 gap-4">
        <div className="card p-6 bg-gradient-to-br from-emerald-50 to-emerald-100 border-emerald-200">
          <div className="text-sm text-slate-600 font-medium mb-1">GROWTH HEALTH</div>
          <div className="text-3xl font-bold text-emerald-900 mb-2">{judgment.growth_health.toUpperCase()}</div>
          <HealthBadge health={judgment.growth_health} />
        </div>

        <div className="card p-6 bg-gradient-to-br from-orange-50 to-orange-100 border-orange-200">
          <div className="text-sm text-slate-600 font-medium mb-1">DISTORTION SEVERITY</div>
          <div className="text-3xl font-bold text-orange-900 mb-2">{judgment.distortion_severity.toUpperCase()}</div>
          <SeverityBadge severity={judgment.distortion_severity} />
        </div>

        <div className="card p-6 bg-gradient-to-br from-blue-50 to-blue-100 border-blue-200">
          <div className="text-sm text-slate-600 font-medium mb-1">STRATEGIC SUSTAINABILITY</div>
          <div className="text-3xl font-bold text-blue-900 mb-2">{judgment.strategic_sustainability.toUpperCase()}</div>
          <SeverityBadge severity={judgment.strategic_sustainability} />
        </div>

        <div className="card p-6 bg-gradient-to-br from-slate-50 to-slate-100 border-slate-200">
          <div className="text-sm text-slate-600 font-medium mb-1">CONFIDENCE</div>
          <div className="text-3xl font-bold text-slate-900 mb-2">{(judgment.confidence * 100).toFixed(0)}%</div>
          <ConfidenceBar confidence={judgment.confidence} />
        </div>
      </div>

      {/* Executive Interpretation */}
      <div className="card p-6">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Executive Interpretation</h2>
        <p className="text-slate-700 leading-relaxed">{judgment.executive_interpretation}</p>
      </div>

      {/* Recommended Action */}
      <div className="card p-6 bg-blue-50 border-blue-200">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Recommended Action</h2>
        <p className="text-slate-700 text-lg mb-4">{judgment.recommended_action}</p>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <div className="font-medium text-slate-600">Owner</div>
            <div className="font-bold text-slate-900">{judgment.owner}</div>
          </div>
          <div>
            <div className="font-medium text-slate-600">Timing</div>
            <div className="font-bold text-slate-900">{judgment.timing}</div>
          </div>
        </div>
      </div>

      {/* Strongest Judgment Drivers */}
      <div className="card p-6">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Why This Judgment?</h2>
        <ul className="space-y-2">
          {judgment.strongest_judgment_drivers.map((driver, idx) => (
            <li key={idx} className="flex gap-3">
              <span className="text-emerald-600 font-bold">✓</span>
              <span className="text-slate-700">{driver}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* What Leadership Should NOT Assume */}
      <div className="card p-6 bg-red-50 border-red-200">
        <h2 className="text-xl font-bold text-slate-900 mb-4">⚠ What Leadership Should NOT Assume</h2>
        <ul className="space-y-2">
          {judgment.what_leadership_should_not_assume.map((item, idx) => (
            <li key={idx} className="flex gap-3">
              <span className="text-red-600 font-bold">✗</span>
              <span className="text-slate-700">{item}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Next Actions */}
      <div className="card p-6 bg-amber-50 border-amber-200">
        <h2 className="text-xl font-bold text-slate-900 mb-4">Required Next Action</h2>
        <p className="text-slate-700 mb-4">{judgment.required_next_action}</p>
      </div>

      {/* Risk Flags */}
      {judgment.executive_risk_flags && judgment.executive_risk_flags.length > 0 && (
        <div className="card p-6 bg-orange-50 border-orange-200">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Executive Risk Flags</h2>
          <ul className="space-y-2">
            {judgment.executive_risk_flags.map((flag, idx) => (
              <li key={idx} className="flex gap-3">
                <span className="text-orange-600 font-bold">⚠</span>
                <span className="text-slate-700">{flag}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}

function TabHumanReview({ caseData, humanNotes, setHumanNotes, onApprove, onReanalyze, agents }) {
  if (caseData.status === 'Draft') {
    return (
      <div className="card bg-slate-100 p-6 text-center">
        <p className="text-slate-700">Start the analysis workflow first.</p>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="card p-6 bg-blue-50 border-blue-200">
        <h2 className="text-xl font-bold text-slate-900 mb-2">Human Review & Approval</h2>
        <p className="text-slate-700">
          Review the agent analysis and provide your judgment before finalizing this case.
        </p>
      </div>

      {agents.agent_6 && (
        <div className="card p-6">
          <h3 className="font-bold text-slate-900 mb-4">Executive Summary</h3>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <div className="text-sm text-slate-600">Growth Health</div>
              <HealthBadge health={agents.agent_6.growth_health} />
            </div>
            <div>
              <div className="text-sm text-slate-600">Distortion Severity</div>
              <SeverityBadge severity={agents.agent_6.distortion_severity} />
            </div>
          </div>
          <p className="text-slate-700">{agents.agent_6.executive_interpretation}</p>
        </div>
      )}

      <div className="card p-6">
        <label className="block text-sm font-medium text-slate-700 mb-2">
          Your Review Notes (Optional)
        </label>
        <textarea
          value={humanNotes}
          onChange={(e) => setHumanNotes(e.target.value)}
          placeholder="Add your observations, modifications, or clarifications..."
          rows={6}
          className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
        />
      </div>

      <div className="flex gap-4 justify-between">
        {caseData.status === 'Needs Review' && !caseData.human_review_approved && (
          <>
            <button onClick={onReanalyze} className="btn btn-secondary">
              Request Re-Analysis
            </button>
            <button onClick={onApprove} className="btn btn-primary">
              Approve & Finalize Case
            </button>
          </>
        )}
        {caseData.human_review_approved && (
          <div className="card bg-emerald-50 border-emerald-200 p-4 w-full text-center">
            <CheckCircle className="inline-block text-emerald-600 mb-2" size={32} />
            <p className="text-emerald-800 font-medium">✓ Case Finalized</p>
            <p className="text-sm text-emerald-700 mt-1">
              Approved at {new Date(caseData.finalized_at).toLocaleString()}
            </p>
          </div>
        )}
      </div>
    </div>
  )
}

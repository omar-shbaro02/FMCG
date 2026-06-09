import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { caseAPI } from '../hooks/useAPI'
import { AlertCircle, Sparkles } from 'lucide-react'

const sampleCase = {
  promotion_id: `PROMO-DEMO-${Date.now()}`,
  brand: 'PremiumBeverage Inc',
  category: 'Beverages - Premium',
  sku: 'PB-PREMIUM-500ML',
  channel: 'Modern Trade',
  key_account: 'Premium Retailer A',
  region: 'Metro',
  promotion_period_start: '2026-02-01',
  promotion_period_end: '2026-02-14',
  campaign_objective: 'EOY Volume Push',
  promotion_type: 'Heavy Discount 25% + Trade Spend',
  baseline_sales_volume: 45000,
  promotion_sales_volume: 156000,
  uplift_percent: 246.7,
  key_account_contribution_percent: 78,
  channel_contribution_percent: 72,
  num_participating_customers: 145,
  sell_in_volume: 160000,
  sell_out_volume: 78000,
  post_promotion_demand: 32000,
  repeat_order_behavior: { repeat_rate: 0.21, trend: 'sharply_declining' },
  inventory_impact: { shelf_inventory_increase: '68%', warehouse_buildup: true },
  replenishment_issues: 'Excessive one-time orders. Normal replenishment delayed.',
  forecast_variance: 48.3,
  discount_percent: 25,
  trade_spend: 285000,
  gross_margin_before: 48,
  gross_margin_during: 8.5,
  management_notes: 'Major retailer negotiated aggressively. Trade loading suspected.',
  data_quality_confidence: 85,
}

export default function NewCase() {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const [formData, setFormData] = useState({
    promotion_id: '',
    brand: '',
    category: '',
    sku: '',
    channel: '',
    key_account: '',
    region: '',
    promotion_period_start: '',
    promotion_period_end: '',
    campaign_objective: '',
    promotion_type: '',
    baseline_sales_volume: 0,
    promotion_sales_volume: 0,
    uplift_percent: 0,
    key_account_contribution_percent: 0,
    channel_contribution_percent: 0,
    num_participating_customers: 0,
    sell_in_volume: 0,
    sell_out_volume: 0,
    post_promotion_demand: 0,
    repeat_order_behavior: {},
    inventory_impact: {},
    replenishment_issues: '',
    forecast_variance: 0,
    discount_percent: 0,
    trade_spend: 0,
    gross_margin_before: 0,
    gross_margin_during: 0,
    management_notes: '',
    data_quality_confidence: 80,
  })

  const handleChange = (e) => {
    const { name, value, type } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: type === 'number' || type === 'range'
        ? value === '' ? '' : Number(value)
        : value
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError(null)

    try {
      const result = await caseAPI.createCase(formData)
      await caseAPI.analyzeCase(result.case.id)
      navigate(`/cases/${result.case.id}`)
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 max-w-4xl">
      <div>
        <h1 className="text-4xl font-bold text-slate-900">Create New Promotion Case</h1>
        <p className="text-slate-600 mt-2">Enter promotion details for analysis</p>
        <button
          type="button"
          onClick={() => setFormData({ ...sampleCase, promotion_id: `PROMO-DEMO-${Date.now()}` })}
          className="btn btn-secondary flex items-center gap-2 mt-4"
        >
          <Sparkles size={16} />
          Load Demo Case
        </button>
      </div>

      {error && (
        <div className="card bg-red-50 border-red-200 p-4 flex gap-3">
          <AlertCircle className="text-red-600 flex-shrink-0" size={20} />
          <div className="text-red-800">{error}</div>
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Promotion Identification */}
        <section className="card p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Promotion Identification</h2>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Promotion ID *</label>
              <input
                type="text"
                name="promotion_id"
                value={formData.promotion_id}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Brand *</label>
              <input
                type="text"
                name="brand"
                value={formData.brand}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Category *</label>
              <input
                type="text"
                name="category"
                value={formData.category}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
          </div>
        </section>

        {/* SKU & Channel */}
        <section className="card p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Channel & Market</h2>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">SKU *</label>
              <input
                type="text"
                name="sku"
                value={formData.sku}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Channel *</label>
              <input
                type="text"
                name="channel"
                value={formData.channel}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Key Account</label>
              <input
                type="text"
                name="key_account"
                value={formData.key_account}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Region *</label>
              <input
                type="text"
                name="region"
                value={formData.region}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
          </div>
        </section>

        {/* Promotion Timing */}
        <section className="card p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Promotion Period</h2>
          <div className="grid grid-cols-4 gap-4">
            <div className="col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-1">Start Date *</label>
              <input
                type="date"
                name="promotion_period_start"
                value={formData.promotion_period_start}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div className="col-span-2">
              <label className="block text-sm font-medium text-slate-700 mb-1">End Date *</label>
              <input
                type="date"
                name="promotion_period_end"
                value={formData.promotion_period_end}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
          </div>
        </section>

        {/* Campaign Details */}
        <section className="card p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Campaign Details</h2>
          <div className="grid grid-cols-2 gap-4 mb-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Campaign Objective *</label>
              <input
                type="text"
                name="campaign_objective"
                value={formData.campaign_objective}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
                placeholder="e.g., Volume Growth, Market Share, Seasonal"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Promotion Type *</label>
              <input
                type="text"
                name="promotion_type"
                value={formData.promotion_type}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
                placeholder="e.g., Discount, Buy 2 Get 1, Bundle"
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">Management Notes</label>
            <textarea
              name="management_notes"
              value={formData.management_notes}
              onChange={handleChange}
              rows={3}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
            />
          </div>
        </section>

        {/* Sales Metrics */}
        <section className="card p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Sales Metrics</h2>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Baseline Sales Volume (units) *</label>
              <input
                type="number"
                name="baseline_sales_volume"
                value={formData.baseline_sales_volume}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Promotion Sales Volume (units) *</label>
              <input
                type="number"
                name="promotion_sales_volume"
                value={formData.promotion_sales_volume}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Uplift % *</label>
              <input
                type="number"
                name="uplift_percent"
                value={formData.uplift_percent}
                onChange={handleChange}
                required
                step="0.1"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
          </div>
        </section>

        {/* Concentration Metrics */}
        <section className="card p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Concentration Metrics</h2>
          <div className="grid grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Key Account Contribution % *</label>
              <input
                type="number"
                name="key_account_contribution_percent"
                value={formData.key_account_contribution_percent}
                onChange={handleChange}
                required
                step="0.1"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Channel Contribution % *</label>
              <input
                type="number"
                name="channel_contribution_percent"
                value={formData.channel_contribution_percent}
                onChange={handleChange}
                required
                step="0.1"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Participating Customers/Stores *</label>
              <input
                type="number"
                name="num_participating_customers"
                value={formData.num_participating_customers}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
          </div>
        </section>

        {/* Inventory & Supply Chain */}
        <section className="card p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Inventory & Supply Chain</h2>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Sell-In Volume (units) *</label>
              <input
                type="number"
                name="sell_in_volume"
                value={formData.sell_in_volume}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Sell-Out Volume (units) *</label>
              <input
                type="number"
                name="sell_out_volume"
                value={formData.sell_out_volume}
                onChange={handleChange}
                required
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Post-Promotion Demand *</label>
              <input
                type="number"
                name="post_promotion_demand"
                value={formData.post_promotion_demand}
                onChange={handleChange}
                required
                step="0.1"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Forecast Variance % *</label>
              <input
                type="number"
                name="forecast_variance"
                value={formData.forecast_variance}
                onChange={handleChange}
                required
                step="0.1"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
          </div>
          <div className="mt-4">
            <label className="block text-sm font-medium text-slate-700 mb-1">Replenishment Issues</label>
            <input
              type="text"
              name="replenishment_issues"
              value={formData.replenishment_issues}
              onChange={handleChange}
              className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
            />
          </div>
        </section>

        {/* Financial Metrics */}
        <section className="card p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Financial Metrics</h2>
          <div className="grid grid-cols-4 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Discount % *</label>
              <input
                type="number"
                name="discount_percent"
                value={formData.discount_percent}
                onChange={handleChange}
                required
                step="0.1"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Trade Spend ($) *</label>
              <input
                type="number"
                name="trade_spend"
                value={formData.trade_spend}
                onChange={handleChange}
                required
                step="0.01"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Gross Margin Before % *</label>
              <input
                type="number"
                name="gross_margin_before"
                value={formData.gross_margin_before}
                onChange={handleChange}
                required
                step="0.1"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Gross Margin During % *</label>
              <input
                type="number"
                name="gross_margin_during"
                value={formData.gross_margin_during}
                onChange={handleChange}
                required
                step="0.1"
                className="w-full px-3 py-2 border border-slate-300 rounded-lg focus:ring-2 focus:ring-slate-900 focus:border-transparent"
              />
            </div>
          </div>
        </section>

        {/* Data Quality */}
        <section className="card p-6">
          <h2 className="text-xl font-bold text-slate-900 mb-4">Data Quality</h2>
          <div>
            <label className="block text-sm font-medium text-slate-700 mb-1">
              Data Quality / Reporting Confidence (0-100) *
            </label>
            <div className="flex gap-4 items-center">
              <input
                type="range"
                name="data_quality_confidence"
                min="0"
                max="100"
                value={formData.data_quality_confidence}
                onChange={handleChange}
                className="flex-1"
              />
              <span className="text-lg font-bold text-slate-900 min-w-12">
                {formData.data_quality_confidence}%
              </span>
            </div>
          </div>
        </section>

        {/* Submit Buttons */}
        <div className="flex gap-4 justify-between">
          <button type="button" onClick={() => navigate('/')} className="btn btn-secondary">
            Cancel
          </button>
          <button
            type="submit"
            disabled={loading}
            className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Creating...' : 'Create Case & Start Analysis'}
          </button>
        </div>
      </form>
    </div>
  )
}

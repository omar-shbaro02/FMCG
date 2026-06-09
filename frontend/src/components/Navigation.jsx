import React from 'react'
import { Link } from 'react-router-dom'
import { Brain } from 'lucide-react'

export default function Navigation() {
  return (
    <nav className="bg-slate-900 text-white shadow-lg">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 text-2xl font-bold">
            <Brain size={32} />
            <span>Trade Promotion Intelligence</span>
          </Link>
          <div className="flex gap-6">
            <Link to="/" className="hover:text-slate-300 transition">Dashboard</Link>
            <Link to="/cases/new" className="hover:text-slate-300 transition">New Case</Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

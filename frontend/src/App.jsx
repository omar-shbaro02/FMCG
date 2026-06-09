import React, { useState, useEffect } from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'
import Navigation from './components/Navigation'
import Dashboard from './pages/Dashboard'
import NewCase from './pages/NewCase'
import CaseDetail from './pages/CaseDetail'

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-slate-50">
        <Navigation />
        <main className="container mx-auto px-4 py-8">
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/cases/new" element={<NewCase />} />
            <Route path="/cases/:caseId" element={<CaseDetail />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  )
}

export default App

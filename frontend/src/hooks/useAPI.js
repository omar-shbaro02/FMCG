import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || '/api'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

apiClient.interceptors.response.use(
  response => response,
  error => {
    const detail = error.response?.data?.detail
    if (detail) {
      error.message = Array.isArray(detail)
        ? detail.map(item => item.msg || JSON.stringify(item)).join(', ')
        : String(detail)
    }
    return Promise.reject(error)
  }
)

export const caseAPI = {
  // Get all cases
  getCases: async () => {
    const response = await apiClient.get('/cases')
    return response.data
  },
  
  // Get single case
  getCase: async (caseId) => {
    const response = await apiClient.get(`/cases/${caseId}`)
    return response.data
  },
  
  // Create new case
  createCase: async (caseData) => {
    const response = await apiClient.post('/cases', caseData)
    return response.data
  },
  
  // Start analysis
  analyzeCase: async (caseId) => {
    const response = await apiClient.post(`/cases/${caseId}/analyze`)
    return response.data
  },
  
  // Approve case
  approveCase: async (caseId, notes, override = false) => {
    const response = await apiClient.post(`/cases/${caseId}/approve`, {
      human_notes: notes,
      override: override,
    })
    return response.data
  },
  
  // Request re-analysis
  requestReanalysis: async (caseId, reason) => {
    const response = await apiClient.post(`/cases/${caseId}/request-reanalysis`, {
      reason: reason,
    })
    return response.data
  },
}

export default apiClient

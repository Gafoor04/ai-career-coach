import axios from 'axios'
import {
  AuthToken,
  LoginRequest,
  RegisterRequest,
  User,
  InterviewStartRequest,
  InterviewStartResponse,
  AnswerSubmitRequest,
  AnswerSubmitResponse,
  SessionSummary,
  SessionHistoryResponse,
  SessionDetail,
} from '@/types'

const api = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' },
})

// ─── REQUEST INTERCEPTOR — attach token ──────────────────────────────────────
api.interceptors.request.use((config) => {
  if (typeof window !== 'undefined') {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
  }
  return config
})

// ─── RESPONSE INTERCEPTOR — handle 401 ───────────────────────────────────────
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token')
        localStorage.removeItem('user')
        window.location.href = '/auth/login'
      }
    }
    return Promise.reject(error)
  }
)

// ─── AUTH API ─────────────────────────────────────────────────────────────────

export const authAPI = {
  register: async (data: RegisterRequest): Promise<User> => {
    const res = await api.post<User>('/auth/register', data)
    return res.data
  },

  login: async (data: LoginRequest): Promise<AuthToken> => {
    const res = await api.post<AuthToken>('/auth/login', data)
    return res.data
  },

  getMe: async (): Promise<User> => {
    const res = await api.get<User>('/auth/me')
    return res.data
  },
}

// ─── INTERVIEW API ────────────────────────────────────────────────────────────

export const interviewAPI = {
  start: async (data: InterviewStartRequest): Promise<InterviewStartResponse> => {
    const res = await api.post<InterviewStartResponse>('/interview/start', data)
    return res.data
  },

  submitAnswer: async (data: AnswerSubmitRequest): Promise<AnswerSubmitResponse> => {
    const res = await api.post<AnswerSubmitResponse>('/interview/answer', data)
    return res.data
  },

  getSummary: async (sessionId: string): Promise<SessionSummary> => {
    const res = await api.get<SessionSummary>(`/interview/summary/${sessionId}`)
    return res.data
  },

  getHistory: async (page = 1, limit = 10): Promise<SessionHistoryResponse> => {
    const res = await api.get<SessionHistoryResponse>(
      `/interview/history?page=${page}&limit=${limit}`
    )
    return res.data
  },

  getSession: async (sessionId: string): Promise<SessionDetail> => {
    const res = await api.get<SessionDetail>(`/interview/session/${sessionId}`)
    return res.data
  },
  resumeSession: async (sessionId: string) => {
  const res = await api.get(`/interview/session/${sessionId}/resume`)
  return res.data
},

abandonSession: async (sessionId: string) => {
  const res = await api.patch(`/interview/session/${sessionId}/abandon`)
  return res.data
},

getStats: async () => {
  const res = await api.get('/interview/stats')
  return res.data
},
}

export default api
export const roadmapAPI = {
  generate: async (data: {
    target_role: string
    experience_level: string
    current_skills: string[]
  }) => {
    const res = await api.post('/roadmap/generate', data)
    return res.data
  },

  getAll: async () => {
    const res = await api.get('/roadmap/')
    return res.data
  },

  getOne: async (id: string) => {
    const res = await api.get(`/roadmap/${id}`)
    return res.data
  },

  delete: async (id: string) => {
    const res = await api.delete(`/roadmap/${id}`)
    return res.data
  },
}
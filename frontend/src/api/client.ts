import axios from 'axios'
import type { Meeting, Transcript, Summary, Task, ProgressReport } from '../types'

const api = axios.create({ baseURL: '/api' })

// Meetings
export const createMeeting = (data: { title: string; description?: string }) =>
  api.post<Meeting>('/meetings', data).then((r) => r.data)

export const getMeetings = () =>
  api.get<Meeting[]>('/meetings').then((r) => r.data)

export const getMeeting = (id: number) =>
  api.get<Meeting>(`/meetings/${id}`).then((r) => r.data)

export const deleteMeeting = (id: number) =>
  api.delete(`/meetings/${id}`)

export const uploadAudio = (meetingId: number, file: File) => {
  const form = new FormData()
  form.append('file', file)
  return api.post<Meeting>(`/meetings/${meetingId}/upload`, form).then((r) => r.data)
}

export const getMeetingStatus = (id: number) =>
  api.get<{ status: string }>(`/meetings/${id}/status`).then((r) => r.data)

// Participants
export const getParticipants = (meetingId: number) =>
  api.get(`/meetings/${meetingId}/participants`).then((r) => r.data)

export const updateParticipant = (meetingId: number, participantId: number, data: { name?: string; email?: string }) =>
  api.put(`/meetings/${meetingId}/participants/${participantId}`, data).then((r) => r.data)

// Transcripts
export const getTranscript = (meetingId: number) =>
  api.get<Transcript>(`/meetings/${meetingId}/transcript`).then((r) => r.data)

// Summary
export const getSummary = (meetingId: number) =>
  api.get<Summary>(`/meetings/${meetingId}/summary`).then((r) => r.data)

export const regenerateSummary = (meetingId: number) =>
  api.post(`/meetings/${meetingId}/summary/regenerate`)

// Tasks
export const getMeetingTasks = (meetingId: number) =>
  api.get<Task[]>(`/meetings/${meetingId}/tasks`).then((r) => r.data)

export const getAllTasks = (status?: string) =>
  api.get<Task[]>('/tasks', { params: status ? { status } : {} }).then((r) => r.data)

export const updateTask = (taskId: number, data: Partial<Task>) =>
  api.put<Task>(`/tasks/${taskId}`, data).then((r) => r.data)

// Reports
export const getReports = () =>
  api.get<ProgressReport[]>('/reports').then((r) => r.data)

export const generateReport = (data: { meeting_id?: number; report_type?: string }) =>
  api.post('/reports/generate', data)

export const getReport = (id: number) =>
  api.get<ProgressReport>(`/reports/${id}`).then((r) => r.data)

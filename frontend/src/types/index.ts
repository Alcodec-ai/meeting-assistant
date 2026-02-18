export type MeetingStatus = 'uploading' | 'processing' | 'completed' | 'failed'
export type TaskPriority = 'low' | 'medium' | 'high'
export type TaskStatus = 'pending' | 'in_progress' | 'completed'

export interface Meeting {
  id: number
  title: string
  description: string | null
  date: string
  duration_seconds: number | null
  status: MeetingStatus
  created_at: string
  updated_at: string
  participants?: Participant[]
}

export interface Participant {
  id: number
  name: string
  email: string | null
  speaker_label: string | null
}

export interface TranscriptSegment {
  id: number
  speaker_label: string
  participant_name: string | null
  start_time: number
  end_time: number
  text: string
  confidence: number | null
  segment_order: number
}

export interface Transcript {
  meeting_id: number
  segments: TranscriptSegment[]
  full_text: string
}

export interface Summary {
  id: number
  meeting_id: number
  full_summary: string
  key_points: string[]
  decisions: string[]
  created_at: string
}

export interface Task {
  id: number
  meeting_id: number
  assignee_id: number | null
  assignee_name: string | null
  title: string
  description: string | null
  priority: TaskPriority
  status: TaskStatus
  due_date: string | null
  created_at: string
  updated_at: string
}

export interface ProgressReport {
  id: number
  meeting_id: number | null
  report_type: string
  content: Record<string, unknown>
  generated_at: string
}

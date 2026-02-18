import { useEffect, useState } from 'react'
import { useParams, Link } from 'react-router-dom'
import { FiArrowLeft, FiUpload, FiRefreshCw } from 'react-icons/fi'
import type { Meeting, Transcript, Summary, Task } from '../../types'
import { getMeeting, uploadAudio, getMeetingStatus, getTranscript, getSummary, getMeetingTasks, regenerateSummary } from '../../api/client'
import TranscriptViewer from '../TranscriptViewer/TranscriptViewer'
import TaskList from '../TaskBoard/TaskList'

export default function MeetingDetail() {
  const { id } = useParams<{ id: string }>()
  const meetingId = Number(id)

  const [meeting, setMeeting] = useState<Meeting | null>(null)
  const [transcript, setTranscript] = useState<Transcript | null>(null)
  const [summary, setSummary] = useState<Summary | null>(null)
  const [tasks, setTasks] = useState<Task[]>([])
  const [activeTab, setActiveTab] = useState<'transcript' | 'summary' | 'tasks'>('transcript')

  const load = async () => {
    const m = await getMeeting(meetingId)
    setMeeting(m)

    if (m.status === 'completed') {
      const [t, s, tk] = await Promise.all([
        getTranscript(meetingId).catch(() => null),
        getSummary(meetingId).catch(() => null),
        getMeetingTasks(meetingId).catch(() => []),
      ])
      setTranscript(t)
      setSummary(s)
      setTasks(tk)
    }
  }

  useEffect(() => { load() }, [meetingId])

  // Poll for status while processing
  useEffect(() => {
    if (!meeting || meeting.status !== 'processing') return
    const interval = setInterval(async () => {
      const { status } = await getMeetingStatus(meetingId)
      if (status !== 'processing') {
        clearInterval(interval)
        load()
      }
    }, 5000)
    return () => clearInterval(interval)
  }, [meeting?.status])

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    await uploadAudio(meetingId, file)
    load()
  }

  if (!meeting) return <div className="text-center py-12 text-gray-500">Yükleniyor...</div>

  const tabs = [
    { key: 'transcript' as const, label: 'Transkript' },
    { key: 'summary' as const, label: 'Özet' },
    { key: 'tasks' as const, label: `Görevler (${tasks.length})` },
  ]

  return (
    <div>
      <Link to="/" className="flex items-center gap-2 text-sm text-gray-500 hover:text-gray-700 mb-4">
        <FiArrowLeft /> Toplantılara Dön
      </Link>

      <div className="bg-white rounded-lg border border-gray-200 p-6 mb-6">
        <div className="flex items-start justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{meeting.title}</h1>
            {meeting.description && <p className="text-gray-500 mt-1">{meeting.description}</p>}
            <div className="flex items-center gap-4 mt-3 text-sm text-gray-400">
              <span>{new Date(meeting.date).toLocaleDateString('tr-TR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
              {meeting.duration_seconds && <span>{Math.round(meeting.duration_seconds / 60)} dakika</span>}
              <span className={`font-medium ${meeting.status === 'completed' ? 'text-green-500' : meeting.status === 'processing' ? 'text-blue-500' : meeting.status === 'failed' ? 'text-red-500' : 'text-yellow-500'}`}>
                {meeting.status === 'completed' ? 'Tamamlandı' : meeting.status === 'processing' ? 'İşleniyor...' : meeting.status === 'failed' ? 'Hata' : 'Yükleniyor'}
              </span>
            </div>
          </div>
          {meeting.status === 'uploading' && (
            <label className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 cursor-pointer text-sm">
              <FiUpload /> Ses Yükle
              <input type="file" accept="audio/*" onChange={handleUpload} className="hidden" />
            </label>
          )}
        </div>
      </div>

      {meeting.status === 'processing' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <FiRefreshCw className="animate-spin mx-auto mb-2 text-blue-500" size={24} />
          <p className="text-blue-700 font-medium">Ses dosyası işleniyor...</p>
          <p className="text-sm text-blue-500 mt-1">Transkripsiyon ve analiz devam ediyor. Bu işlem birkaç dakika sürebilir.</p>
        </div>
      )}

      {meeting.status === 'failed' && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
          <p className="text-red-700 font-medium">İşleme sırasında bir hata oluştu.</p>
          <p className="text-sm text-red-500 mt-1">Lütfen ses dosyasını tekrar yüklemeyi deneyin.</p>
        </div>
      )}

      {meeting.status === 'completed' && (
        <>
          <div className="flex gap-1 mb-4 border-b border-gray-200">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                onClick={() => setActiveTab(tab.key)}
                className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
                  activeTab === tab.key
                    ? 'border-indigo-600 text-indigo-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>

          {activeTab === 'transcript' && transcript && (
            <TranscriptViewer transcript={transcript} />
          )}

          {activeTab === 'summary' && summary && (
            <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
              <div className="flex items-center justify-between">
                <h2 className="text-lg font-bold">Toplantı Özeti</h2>
                <button
                  onClick={() => regenerateSummary(meetingId)}
                  className="flex items-center gap-1 text-sm text-indigo-600 hover:text-indigo-700"
                >
                  <FiRefreshCw size={14} /> Yeniden Oluştur
                </button>
              </div>
              <p className="text-gray-700 whitespace-pre-wrap">{summary.full_summary}</p>

              {summary.key_points.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Önemli Noktalar</h3>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    {summary.key_points.map((p, i) => <li key={i}>{p}</li>)}
                  </ul>
                </div>
              )}

              {summary.decisions.length > 0 && (
                <div>
                  <h3 className="font-semibold text-gray-900 mb-2">Alınan Kararlar</h3>
                  <ul className="list-disc list-inside space-y-1 text-gray-600">
                    {summary.decisions.map((d, i) => <li key={i}>{d}</li>)}
                  </ul>
                </div>
              )}
            </div>
          )}

          {activeTab === 'tasks' && (
            <TaskList tasks={tasks} onUpdate={load} />
          )}
        </>
      )}
    </div>
  )
}

import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { FiPlus, FiTrash2, FiClock, FiCheckCircle, FiLoader, FiAlertCircle } from 'react-icons/fi'
import type { Meeting } from '../../types'
import { getMeetings, deleteMeeting } from '../../api/client'
import NewMeetingModal from './NewMeetingModal'

const statusConfig = {
  uploading: { icon: FiClock, color: 'text-yellow-500', label: 'Yükleniyor' },
  processing: { icon: FiLoader, color: 'text-blue-500', label: 'İşleniyor' },
  completed: { icon: FiCheckCircle, color: 'text-green-500', label: 'Tamamlandı' },
  failed: { icon: FiAlertCircle, color: 'text-red-500', label: 'Hata' },
}

export default function MeetingList() {
  const [meetings, setMeetings] = useState<Meeting[]>([])
  const [showModal, setShowModal] = useState(false)
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      setMeetings(await getMeetings())
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  const handleDelete = async (id: number) => {
    if (!confirm('Bu toplantıyı silmek istediğinizden emin misiniz?')) return
    await deleteMeeting(id)
    load()
  }

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Toplantılar</h1>
        <button
          onClick={() => setShowModal(true)}
          className="flex items-center gap-2 bg-indigo-600 text-white px-4 py-2 rounded-lg hover:bg-indigo-700 transition-colors"
        >
          <FiPlus /> Yeni Toplantı
        </button>
      </div>

      {loading ? (
        <div className="text-center py-12 text-gray-500">Yükleniyor...</div>
      ) : meetings.length === 0 ? (
        <div className="text-center py-12 text-gray-500">
          Henüz toplantı yok. Yeni bir toplantı oluşturun.
        </div>
      ) : (
        <div className="grid gap-4">
          {meetings.map((m) => {
            const st = statusConfig[m.status]
            const StatusIcon = st.icon
            return (
              <Link
                key={m.id}
                to={`/meetings/${m.id}`}
                className="bg-white rounded-lg border border-gray-200 p-5 hover:shadow-md transition-shadow flex items-center justify-between"
              >
                <div>
                  <h3 className="font-semibold text-gray-900">{m.title}</h3>
                  {m.description && (
                    <p className="text-sm text-gray-500 mt-1">{m.description}</p>
                  )}
                  <div className="flex items-center gap-4 mt-2 text-sm text-gray-400">
                    <span>{new Date(m.date).toLocaleDateString('tr-TR')}</span>
                    {m.duration_seconds && (
                      <span>{Math.round(m.duration_seconds / 60)} dk</span>
                    )}
                  </div>
                </div>
                <div className="flex items-center gap-3">
                  <span className={`flex items-center gap-1 text-sm ${st.color}`}>
                    <StatusIcon size={16} />
                    {st.label}
                  </span>
                  <button
                    onClick={(e) => { e.preventDefault(); handleDelete(m.id) }}
                    className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <FiTrash2 size={16} />
                  </button>
                </div>
              </Link>
            )
          })}
        </div>
      )}

      {showModal && (
        <NewMeetingModal
          onClose={() => setShowModal(false)}
          onCreated={() => { setShowModal(false); load() }}
        />
      )}
    </div>
  )
}

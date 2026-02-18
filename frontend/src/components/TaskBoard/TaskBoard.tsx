import { useEffect, useState } from 'react'
import type { Task } from '../../types'
import { getAllTasks } from '../../api/client'
import TaskList from './TaskList'

export default function TaskBoard() {
  const [tasks, setTasks] = useState<Task[]>([])
  const [loading, setLoading] = useState(true)

  const load = async () => {
    setLoading(true)
    try {
      setTasks(await getAllTasks())
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  if (loading) return <div className="text-center py-12 text-gray-500">Yükleniyor...</div>

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Tüm Görevler</h1>
      {tasks.length === 0 ? (
        <p className="text-gray-500 text-center py-12">Henüz görev yok. Toplantı işlendikten sonra görevler otomatik oluşturulacak.</p>
      ) : (
        <TaskList tasks={tasks} onUpdate={load} />
      )}
    </div>
  )
}

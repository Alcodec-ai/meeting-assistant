import { FiUser, FiFlag } from 'react-icons/fi'
import type { Task, TaskStatus } from '../../types'
import { updateTask } from '../../api/client'

interface Props {
  tasks: Task[]
  onUpdate: () => void
}

const statusLabels: Record<TaskStatus, string> = {
  pending: 'Bekleyen',
  in_progress: 'Devam Eden',
  completed: 'Tamamlanan',
}

const priorityConfig = {
  high: { color: 'text-red-500', label: 'Yüksek' },
  medium: { color: 'text-yellow-500', label: 'Orta' },
  low: { color: 'text-green-500', label: 'Düşük' },
}

export default function TaskList({ tasks, onUpdate }: Props) {
  const handleStatusChange = async (taskId: number, status: TaskStatus) => {
    await updateTask(taskId, { status })
    onUpdate()
  }

  const columns: TaskStatus[] = ['pending', 'in_progress', 'completed']

  return (
    <div className="grid grid-cols-3 gap-4">
      {columns.map((status) => {
        const columnTasks = tasks.filter((t) => t.status === status)
        return (
          <div key={status} className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-semibold text-gray-700 mb-3 text-sm">
              {statusLabels[status]} ({columnTasks.length})
            </h3>
            <div className="space-y-3">
              {columnTasks.map((task) => {
                const pri = priorityConfig[task.priority]
                return (
                  <div key={task.id} className="bg-white rounded-lg border border-gray-200 p-3">
                    <p className="font-medium text-sm text-gray-900">{task.title}</p>
                    {task.description && (
                      <p className="text-xs text-gray-500 mt-1">{task.description}</p>
                    )}
                    <div className="flex items-center justify-between mt-2">
                      <div className="flex items-center gap-2 text-xs">
                        {task.assignee_name && (
                          <span className="flex items-center gap-1 text-gray-500">
                            <FiUser size={12} /> {task.assignee_name}
                          </span>
                        )}
                        <span className={`flex items-center gap-1 ${pri.color}`}>
                          <FiFlag size={12} /> {pri.label}
                        </span>
                      </div>
                      <select
                        value={task.status}
                        onChange={(e) => handleStatusChange(task.id, e.target.value as TaskStatus)}
                        className="text-xs border border-gray-200 rounded px-1 py-0.5"
                      >
                        {columns.map((s) => (
                          <option key={s} value={s}>{statusLabels[s]}</option>
                        ))}
                      </select>
                    </div>
                  </div>
                )
              })}
              {columnTasks.length === 0 && (
                <p className="text-xs text-gray-400 text-center py-4">Görev yok</p>
              )}
            </div>
          </div>
        )
      })}
    </div>
  )
}

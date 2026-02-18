import { useEffect, useState } from 'react'
import { FiFileText } from 'react-icons/fi'
import type { ProgressReport } from '../../types'
import { getReports } from '../../api/client'

export default function ReportDashboard() {
  const [reports, setReports] = useState<ProgressReport[]>([])
  const [selected, setSelected] = useState<ProgressReport | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    setLoading(true)
    getReports()
      .then(setReports)
      .finally(() => setLoading(false))
  }, [])

  if (loading) return <div className="text-center py-12 text-gray-500">Yükleniyor...</div>

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Raporlar</h1>

      {reports.length === 0 ? (
        <p className="text-gray-500 text-center py-12">
          Henüz rapor yok. Toplantı detay sayfasından rapor oluşturabilirsiniz.
        </p>
      ) : (
        <div className="grid grid-cols-3 gap-6">
          <div className="col-span-1 space-y-2">
            {reports.map((r) => (
              <button
                key={r.id}
                onClick={() => setSelected(r)}
                className={`w-full text-left p-3 rounded-lg border transition-colors ${
                  selected?.id === r.id
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 bg-white hover:bg-gray-50'
                }`}
              >
                <div className="flex items-center gap-2">
                  <FiFileText className="text-gray-400" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {(r.content as Record<string, string>).title || `Rapor #${r.id}`}
                    </p>
                    <p className="text-xs text-gray-400">
                      {new Date(r.generated_at).toLocaleDateString('tr-TR')}
                    </p>
                  </div>
                </div>
              </button>
            ))}
          </div>

          <div className="col-span-2">
            {selected ? (
              <div className="bg-white rounded-lg border border-gray-200 p-6">
                <h2 className="text-lg font-bold mb-4">
                  {(selected.content as Record<string, string>).title || `Rapor #${selected.id}`}
                </h2>
                <pre className="text-sm text-gray-700 whitespace-pre-wrap">
                  {JSON.stringify(selected.content, null, 2)}
                </pre>
              </div>
            ) : (
              <div className="text-center py-12 text-gray-400">
                Görüntülemek için bir rapor seçin.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

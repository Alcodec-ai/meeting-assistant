import type { Transcript } from '../../types'

interface Props {
  transcript: Transcript
}

const speakerColors = [
  'bg-blue-100 text-blue-800',
  'bg-green-100 text-green-800',
  'bg-purple-100 text-purple-800',
  'bg-orange-100 text-orange-800',
  'bg-pink-100 text-pink-800',
  'bg-teal-100 text-teal-800',
]

function formatTime(seconds: number): string {
  const m = Math.floor(seconds / 60)
  const s = Math.floor(seconds % 60)
  return `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
}

export default function TranscriptViewer({ transcript }: Props) {
  const speakers = [...new Set(transcript.segments.map((s) => s.speaker_label))]
  const colorMap = Object.fromEntries(
    speakers.map((s, i) => [s, speakerColors[i % speakerColors.length]])
  )

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h2 className="text-lg font-bold mb-4">Transkript</h2>

      <div className="flex gap-2 mb-4 flex-wrap">
        {speakers.map((s) => {
          const seg = transcript.segments.find((seg) => seg.speaker_label === s)
          const name = seg?.participant_name || s
          return (
            <span key={s} className={`px-2 py-1 rounded text-xs font-medium ${colorMap[s]}`}>
              {name}
            </span>
          )
        })}
      </div>

      <div className="space-y-3 max-h-[600px] overflow-y-auto">
        {transcript.segments.map((seg) => (
          <div key={seg.id} className="flex gap-3">
            <span className="text-xs text-gray-400 mt-1 w-12 shrink-0 font-mono">
              {formatTime(seg.start_time)}
            </span>
            <div>
              <span className={`inline-block px-2 py-0.5 rounded text-xs font-medium mb-1 ${colorMap[seg.speaker_label]}`}>
                {seg.participant_name || seg.speaker_label}
              </span>
              <p className="text-gray-700 text-sm">{seg.text}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

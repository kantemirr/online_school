import { useEffect, useState } from 'react'

import { Button, Modal } from '../../components/ui'
import { cn } from '../../lib/cn'
import { notify } from '../../lib/toast'
import { useMarkAttendanceMutation, useSessionAttendanceQuery, type Member } from './api'

const STATUSES: { v: string; l: string }[] = [
  { v: 'present', l: 'Был' },
  { v: 'absent', l: 'Нет' },
  { v: 'excused', l: 'Уваж.' },
]

interface AttendanceGridProps {
  open: boolean
  onOpenChange: (o: boolean) => void
  sessionId: number
  members: Member[]
}

export function AttendanceGrid({ open, onOpenChange, sessionId, members }: AttendanceGridProps) {
  const { data: existing } = useSessionAttendanceQuery(sessionId, { skip: !open })
  const [marks, setMarks] = useState<Record<number, string>>({})
  const [mark, { isLoading }] = useMarkAttendanceMutation()

  useEffect(() => {
    if (!open) return
    const init: Record<number, string> = {}
    members.forEach((m) => (init[m.student_id] = 'present'))
    existing?.forEach((a) => (init[a.student_id] = a.status))
    setMarks(init)
  }, [open, existing, members])

  async function submit() {
    const records = members.map((m) => ({ student_id: m.student_id, status: marks[m.student_id] ?? 'present' }))
    try {
      await mark({ session_id: sessionId, records }).unwrap()
      notify.success('Посещаемость сохранена')
      onOpenChange(false)
    } catch {
      notify.error('Не удалось сохранить')
    }
  }

  return (
    <Modal open={open} onOpenChange={onOpenChange} title="Отметить посещаемость">
      <div className="space-y-2">
        {members.map((m) => (
          <div key={m.student_id} className="flex items-center gap-2">
            <span className="flex-1 font-bold text-ink">{m.nickname ?? `#${m.student_id}`}</span>
            <div className="flex gap-1">
              {STATUSES.map((s) => (
                <button
                  key={s.v}
                  onClick={() => setMarks((p) => ({ ...p, [m.student_id]: s.v }))}
                  className={cn(
                    'rounded-md px-2.5 py-1 text-xs font-bold transition',
                    marks[m.student_id] === s.v ? 'bg-brand text-white' : 'bg-cloud text-muted',
                  )}
                >
                  {s.l}
                </button>
              ))}
            </div>
          </div>
        ))}
        {members.length === 0 && <p className="text-sm text-hint">В группе пока нет учеников.</p>}
        <Button fullWidth loading={isLoading} disabled={members.length === 0} onClick={submit}>
          Сохранить
        </Button>
      </div>
    </Modal>
  )
}

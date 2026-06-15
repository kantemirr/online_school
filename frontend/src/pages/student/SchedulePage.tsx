import { Video } from 'lucide-react'

import { Badge, Button, Card, EmptyState, Skeleton } from '../../components/ui'
import { useMyAttendanceQuery, useMyScheduleQuery } from '../../features/scheduling/api'
import { formatDate, formatDateTime } from '../../lib/format'
import { ATTENDANCE_LABEL } from '../../lib/labels'

export function SchedulePage() {
  const { data: schedule, isLoading } = useMyScheduleQuery()
  const { data: attendance } = useMyAttendanceQuery()

  if (isLoading) return <Skeleton className="h-60 w-full rounded-xl" />

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-extrabold text-ink">Расписание</h1>

      {!schedule || schedule.length === 0 ? (
        <EmptyState
          title="Пока нет занятий"
          description="Когда преподаватель добавит тебя в группу, здесь появятся онлайн-занятия."
          mood="idle"
        />
      ) : (
        <div className="space-y-3">
          {schedule.map((s) => (
            <Card key={s.session_id} className="flex flex-wrap items-center gap-3">
              <div className="flex-1">
                <div className="font-bold text-ink">{s.group_name}</div>
                <div className="text-sm text-muted">{formatDateTime(s.starts_at)}</div>
              </div>
              {s.meeting_url && (
                <a href={s.meeting_url} target="_blank" rel="noreferrer">
                  <Button variant="reward">
                    <Video className="h-4 w-4" aria-hidden /> Подключиться
                  </Button>
                </a>
              )}
            </Card>
          ))}
        </div>
      )}

      {attendance && attendance.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-extrabold text-ink">Посещаемость</h2>
          <div className="space-y-2">
            {attendance.map((a) => (
              <Card key={a.session_id} className="flex items-center gap-3 py-3">
                <span className="flex-1 text-sm text-muted">{formatDate(a.starts_at)}</span>
                <Badge tone={a.status === 'present' ? 'success' : a.status === 'excused' ? 'sun' : 'danger'}>
                  {ATTENDANCE_LABEL[a.status]}
                </Badge>
              </Card>
            ))}
          </div>
        </section>
      )}
    </div>
  )
}

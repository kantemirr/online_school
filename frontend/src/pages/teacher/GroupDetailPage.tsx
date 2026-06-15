import { useState } from 'react'

import { BarChart3, CalendarPlus, ClipboardCheck, Trash2, UserPlus, Video } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'

import { Button, Card, EmptyState, Skeleton } from '../../components/ui'
import { AttendanceGrid } from '../../features/scheduling/AttendanceGrid'
import { SessionForm } from '../../features/scheduling/SessionForm'
import { StudentPicker } from '../../features/scheduling/StudentPicker'
import { useDeleteSessionMutation, useGroupQuery, useRemoveMemberMutation } from '../../features/scheduling/api'
import { formatDateTime } from '../../lib/format'
import { notify } from '../../lib/toast'

export function GroupDetailPage() {
  const { id } = useParams()
  const gid = Number(id)
  const { data, isLoading, isError } = useGroupQuery(gid)
  const [removeMember] = useRemoveMemberMutation()
  const [deleteSession] = useDeleteSessionMutation()
  const [pickerOpen, setPickerOpen] = useState(false)
  const [sessionOpen, setSessionOpen] = useState(false)
  const [attendanceSession, setAttendanceSession] = useState<number | null>(null)

  if (isLoading) return <Skeleton className="h-72 w-full rounded-xl" />
  if (isError || !data) {
    return (
      <EmptyState
        title="Группа недоступна"
        mood="sad"
        action={
          <Link to="/teacher">
            <Button variant="secondary">К группам</Button>
          </Link>
        }
      />
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h1 className="text-2xl font-extrabold text-ink">{data.name}</h1>
        <Link to={`/teacher/groups/${gid}/analytics`}>
          <Button variant="secondary">
            <BarChart3 className="h-4 w-4" aria-hidden /> Аналитика
          </Button>
        </Link>
      </div>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-extrabold text-ink">Состав</h2>
          <Button size="sm" onClick={() => setPickerOpen(true)}>
            <UserPlus className="h-4 w-4" aria-hidden /> Добавить
          </Button>
        </div>
        {data.members.length === 0 ? (
          <Card className="text-muted">В группе пока нет учеников.</Card>
        ) : (
          <Card className="p-0">
            <ul className="divide-y divide-line">
              {data.members.map((m) => (
                <li key={m.student_id} className="flex items-center gap-2 px-4 py-2.5">
                  <span className="flex-1 font-bold text-ink">{m.nickname ?? `#${m.student_id}`}</span>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-danger-700"
                    aria-label="Убрать"
                    onClick={async () => {
                      try {
                        await removeMember({ group_id: gid, student_id: m.student_id }).unwrap()
                      } catch {
                        notify.error('Не удалось убрать ученика')
                      }
                    }}
                  >
                    <Trash2 className="h-4 w-4" aria-hidden />
                  </Button>
                </li>
              ))}
            </ul>
          </Card>
        )}
      </section>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-extrabold text-ink">Занятия</h2>
          <Button size="sm" onClick={() => setSessionOpen(true)}>
            <CalendarPlus className="h-4 w-4" aria-hidden /> Добавить
          </Button>
        </div>
        {data.sessions.length === 0 ? (
          <Card className="text-muted">Занятий пока нет.</Card>
        ) : (
          <div className="space-y-2">
            {data.sessions.map((s) => (
              <Card key={s.id} className="flex flex-wrap items-center gap-3">
                <div className="flex-1 font-bold text-ink">{formatDateTime(s.starts_at)}</div>
                {s.meeting_url && (
                  <a href={s.meeting_url} target="_blank" rel="noreferrer">
                    <Button variant="ghost" size="sm" aria-label="Ссылка">
                      <Video className="h-4 w-4" aria-hidden />
                    </Button>
                  </a>
                )}
                <Button variant="secondary" size="sm" onClick={() => setAttendanceSession(s.id)}>
                  <ClipboardCheck className="h-4 w-4" aria-hidden /> Посещаемость
                </Button>
                <Button
                  variant="ghost"
                  size="sm"
                  className="text-danger-700"
                  aria-label="Удалить занятие"
                  onClick={async () => {
                    try {
                      await deleteSession({ session_id: s.id }).unwrap()
                    } catch {
                      notify.error('Не удалось удалить занятие')
                    }
                  }}
                >
                  <Trash2 className="h-4 w-4" aria-hidden />
                </Button>
              </Card>
            ))}
          </div>
        )}
      </section>

      <StudentPicker open={pickerOpen} onOpenChange={setPickerOpen} groupId={gid} />
      <SessionForm open={sessionOpen} onOpenChange={setSessionOpen} groupId={gid} />
      {attendanceSession != null && (
        <AttendanceGrid
          open={attendanceSession != null}
          onOpenChange={(o) => !o && setAttendanceSession(null)}
          sessionId={attendanceSession}
          members={data.members}
        />
      )}
    </div>
  )
}

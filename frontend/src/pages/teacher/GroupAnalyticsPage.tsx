import { Link, useParams } from 'react-router-dom'

import { Button, Card, EmptyState, ProgressBar, Skeleton } from '../../components/ui'
import { useGroupAnalyticsQuery } from '../../features/analytics/api'
import { formatDate } from '../../lib/format'

export function GroupAnalyticsPage() {
  const { id } = useParams()
  const gid = Number(id)
  const { data, isLoading, isError } = useGroupAnalyticsQuery(gid)

  if (isLoading) return <Skeleton className="h-72 w-full rounded-xl" />
  if (isError || !data) {
    return (
      <EmptyState
        title="Нет данных"
        mood="thinking"
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
      <h1 className="text-2xl font-extrabold text-ink">Аналитика: {data.name}</h1>

      <div className="grid grid-cols-3 gap-3">
        <Card className="text-center">
          <div className="text-2xl font-extrabold text-brand">{Math.round(data.avg_progress)}%</div>
          <div className="text-xs text-muted">Средний прогресс</div>
        </Card>
        <Card className="text-center">
          <div className="text-2xl font-extrabold text-teal-700">{Math.round(data.avg_attendance)}%</div>
          <div className="text-xs text-muted">Посещаемость</div>
        </Card>
        <Card className="text-center">
          <div className="text-2xl font-extrabold text-sun-700">{data.active_count}</div>
          <div className="text-xs text-muted">Активных</div>
        </Card>
      </div>

      {data.students.length === 0 ? (
        <Card className="text-muted">В группе нет учеников.</Card>
      ) : (
        <Card className="p-0">
          <ul className="divide-y divide-line">
            {data.students.map((s) => (
              <li key={s.student_id} className="px-4 py-3">
                <div className="flex items-center justify-between">
                  <span className="font-bold text-ink">{s.nickname}</span>
                  <span className="text-xs text-hint">{s.last_active ? formatDate(s.last_active) : 'не заходил'}</span>
                </div>
                <div className="mt-1 flex items-center gap-3">
                  <ProgressBar value={s.progress_pct} className="flex-1" />
                  <span className="whitespace-nowrap text-xs text-muted">
                    {Math.round(s.progress_pct)}% · посещ. {Math.round(s.attendance_rate)}%
                  </span>
                </div>
              </li>
            ))}
          </ul>
        </Card>
      )}
    </div>
  )
}

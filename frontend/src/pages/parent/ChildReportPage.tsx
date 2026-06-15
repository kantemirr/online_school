import { FileDown, Trophy } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'

import { Badge, Button, Card, EmptyState, ProgressBar, Skeleton } from '../../components/ui'
import { useChildReportQuery } from '../../features/analytics/api'
import { formatDate } from '../../lib/format'
import { openReport } from '../../lib/openReport'
import { notify } from '../../lib/toast'
import { useAppSelector } from '../../store/hooks'

export function ChildReportPage() {
  const { id } = useParams()
  const childId = Number(id)
  const token = useAppSelector((s) => s.auth.accessToken)
  const { data, isLoading, isError } = useChildReportQuery(childId)

  if (isLoading) return <Skeleton className="h-72 w-full rounded-xl" />
  if (isError || !data) {
    return (
      <EmptyState
        title="Отчёт недоступен"
        description="Профиль ребёнка не найден."
        mood="sad"
        action={
          <Link to="/parent">
            <Button variant="secondary">На главную</Button>
          </Link>
        }
      />
    )
  }

  async function handleOpen() {
    try {
      await openReport(childId, token)
    } catch {
      notify.error('Не удалось открыть отчёт')
    }
  }

  const att = data.attendance

  return (
    <div className="space-y-6">
      <Card className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <h1 className="text-2xl font-extrabold text-ink">{data.nickname}</h1>
          <p className="text-sm text-muted">
            {data.xp.toLocaleString('ru-RU')} XP · серия {data.streak} дн.
          </p>
        </div>
        <Button onClick={handleOpen}>
          <FileDown className="h-4 w-4" aria-hidden /> Открыть отчёт
        </Button>
      </Card>

      <section>
        <h2 className="mb-3 text-lg font-extrabold text-ink">Прогресс по курсам</h2>
        {data.courses.length === 0 ? (
          <Card className="text-muted">Ребёнок ещё не записан на курсы.</Card>
        ) : (
          <div className="space-y-3">
            {data.courses.map((c) => (
              <Card key={c.course_id}>
                <div className="mb-2 flex items-center justify-between">
                  <span className="font-bold text-ink">{c.title}</span>
                  <span className="text-sm text-hint">средний балл {c.avg_score}</span>
                </div>
                <ProgressBar value={c.progress_pct} />
                <p className="mt-1 text-xs text-hint">
                  {Math.round(c.progress_pct)}% · завершено уроков {c.completed_lessons}
                </p>
              </Card>
            ))}
          </div>
        )}
      </section>

      <section>
        <h2 className="mb-3 text-lg font-extrabold text-ink">Посещаемость</h2>
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          <Card className="text-center">
            <div className="text-2xl font-extrabold text-success-700">{att.present}</div>
            <div className="text-xs text-muted">Присутствий</div>
          </Card>
          <Card className="text-center">
            <div className="text-2xl font-extrabold text-danger-700">{att.absent}</div>
            <div className="text-xs text-muted">Пропусков</div>
          </Card>
          <Card className="text-center">
            <div className="text-2xl font-extrabold text-sun-700">{att.excused}</div>
            <div className="text-xs text-muted">Уважительных</div>
          </Card>
          <Card className="text-center">
            <div className="text-2xl font-extrabold text-brand">{Math.round(att.rate)}%</div>
            <div className="text-xs text-muted">Доля присутствий</div>
          </Card>
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-lg font-extrabold text-ink">Достижения</h2>
        {data.achievements.length === 0 ? (
          <Card className="text-muted">Пока нет достижений.</Card>
        ) : (
          <div className="flex flex-wrap gap-2">
            {data.achievements.map((a) => (
              <Badge key={a.code} tone="sun">
                <Trophy className="h-3.5 w-3.5" aria-hidden /> {a.title}
                {a.earned_at && ` · ${formatDate(a.earned_at)}`}
              </Badge>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

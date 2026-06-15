import { CheckCircle2, Lock, PlayCircle } from 'lucide-react'
import { Link, useParams } from 'react-router-dom'

import { Kodik } from '../../components/mascot/Kodik'
import { Badge, Button, Card, EmptyState, ProgressBar, Skeleton } from '../../components/ui'
import { usePassageQuery } from '../../features/learning/api'
import { cn } from '../../lib/cn'

export function LearnCoursePage() {
  const { courseId } = useParams()
  const cid = Number(courseId)
  const { data, isLoading, isError } = usePassageQuery(cid)

  if (isLoading) return <Skeleton className="h-72 w-full rounded-xl" />
  if (isError || !data) {
    return (
      <EmptyState
        title="Нет доступа к курсу"
        description="Похоже, вы ещё не записаны на этот курс."
        mood="thinking"
        action={
          <Link to={`/courses/${cid}`}>
            <Button variant="secondary">Открыть страницу курса</Button>
          </Link>
        }
      />
    )
  }

  const done = data.status === 'completed'

  return (
    <div className="space-y-6">
      <Card>
        <div className="flex items-center justify-between gap-3">
          <h1 className="text-2xl font-extrabold text-ink">{data.title}</h1>
          {done && <Badge tone="success">Курс пройден</Badge>}
        </div>
        <div className="mt-3">
          <ProgressBar value={data.progress_pct} />
          <p className="mt-2 text-sm text-hint">Прогресс {Math.round(data.progress_pct)}%</p>
        </div>
        {done ? (
          <div className="mt-3 flex items-center gap-3">
            <Kodik mood="celebrate" size={56} aria-hidden />
            <span className="font-bold text-ink">Поздравляем с завершением курса!</span>
          </div>
        ) : (
          data.resume_lesson_id && (
            <Link to={`/learn/lessons/${data.resume_lesson_id}`}>
              <Button variant="reward" className="mt-3">
                Продолжить с текущего урока
              </Button>
            </Link>
          )
        )}
      </Card>

      {data.modules.map((m, mi) => (
        <Card key={m.id}>
          <h3 className="mb-2 font-extrabold text-ink">
            Модуль {mi + 1}. {m.title}
          </h3>
          <ul className="divide-y divide-line">
            {m.lessons.map((l) => {
              const Icon = l.status === 'completed' ? CheckCircle2 : l.locked ? Lock : PlayCircle
              const row = (
                <div className={cn('flex items-center gap-3 py-2.5', l.locked ? 'text-hint' : 'text-ink')}>
                  <Icon
                    className={cn(
                      'h-5 w-5',
                      l.status === 'completed' ? 'text-success' : l.locked ? 'text-hint' : 'text-brand',
                    )}
                    aria-hidden
                  />
                  <span className="flex-1">{l.title}</span>
                  {l.assignment_count > 0 && <span className="text-xs text-hint">{l.assignment_count} зад.</span>}
                </div>
              )
              return (
                <li key={l.id}>
                  {l.locked ? (
                    <div className="cursor-not-allowed" title="Сначала пройди предыдущий урок">
                      {row}
                    </div>
                  ) : (
                    <Link to={`/learn/lessons/${l.id}`} className="block rounded-md px-2 transition hover:bg-cloud">
                      {row}
                    </Link>
                  )}
                </li>
              )
            })}
          </ul>
        </Card>
      ))}
    </div>
  )
}

import { Code2, FileText, ListChecks, type LucideIcon } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { Markdown } from '../../components/markdown/Markdown'
import { useKodik } from '../../components/mascot/KodikProvider'
import { Badge, Button, Card, EmptyState, Skeleton } from '../../components/ui'
import { useCompleteLessonMutation, useLessonQuery } from '../../features/learning/api'
import { notify } from '../../lib/toast'

const TYPE_META: Record<string, { icon: LucideIcon; label: string }> = {
  quiz: { icon: ListChecks, label: 'Квиз' },
  code: { icon: Code2, label: 'Код' },
  project: { icon: FileText, label: 'Проект' },
}

export function LessonPage() {
  const { lessonId } = useParams()
  const lid = Number(lessonId)
  const nav = useNavigate()
  const { react } = useKodik()
  const { data, isLoading, isError } = useLessonQuery(lid)
  const [complete, { isLoading: completing }] = useCompleteLessonMutation()

  if (isLoading) return <Skeleton className="h-72 w-full rounded-xl" />
  if (isError || !data) {
    return (
      <EmptyState
        title="Урок недоступен"
        description="Сначала пройди предыдущие уроки курса."
        mood="thinking"
      />
    )
  }

  async function finish() {
    try {
      const passage = await complete(lid).unwrap()
      react('happy')
      notify.success('Урок завершён!')
      nav(`/learn/${passage.course_id}`)
    } catch {
      notify.error('Не удалось завершить урок')
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between gap-3">
        <h1 className="text-2xl font-extrabold text-ink">{data.title}</h1>
        {data.status === 'completed' && <Badge tone="success">Пройдено</Badge>}
      </div>

      {data.video_url && (
        <Card>
          <div className="aspect-video">
            <iframe
              src={data.video_url}
              className="h-full w-full rounded-md"
              allowFullScreen
              title="Видео урока"
            />
          </div>
        </Card>
      )}

      {data.theory_md && (
        <Card>
          <Markdown>{data.theory_md}</Markdown>
        </Card>
      )}

      {data.assignments.length > 0 && (
        <section>
          <h2 className="mb-3 text-lg font-extrabold text-ink">Задания</h2>
          <div className="space-y-3">
            {data.assignments.map((a) => {
              const meta = TYPE_META[a.type]
              const Icon = meta.icon
              return (
                <Link key={a.id} to={`/assignments/${a.id}`}>
                  <Card className="flex items-center gap-3 transition hover:shadow-pop">
                    <span className="flex h-10 w-10 items-center justify-center rounded-md bg-brand-50 text-brand">
                      <Icon className="h-5 w-5" aria-hidden />
                    </span>
                    <div className="flex-1">
                      <div className="font-bold text-ink">{a.title}</div>
                      <div className="text-xs text-hint">
                        {meta.label} · до {a.max_score} баллов
                      </div>
                    </div>
                  </Card>
                </Link>
              )
            })}
          </div>
        </section>
      )}

      {data.assignments.length === 0 && data.status !== 'completed' && (
        <Button onClick={finish} loading={completing}>
          Завершить урок
        </Button>
      )}
    </div>
  )
}

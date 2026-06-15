import { useState } from 'react'

import { BookOpen } from 'lucide-react'
import { Link, useNavigate, useParams } from 'react-router-dom'

import { Kodik } from '../../components/mascot/Kodik'
import { Badge, Button, Card, EmptyState, Modal, Skeleton } from '../../components/ui'
import { useCourseQuery } from '../../features/catalog/api'
import { useEnrollMutation, useEnrollmentsQuery } from '../../features/learning/api'
import { formatMoney } from '../../lib/format'
import { LEVEL_LABEL, TRACK_LABEL } from '../../lib/labels'
import { notify } from '../../lib/toast'

export function CoursePage() {
  const { id } = useParams()
  const courseId = Number(id)
  const nav = useNavigate()
  const { data: course, isLoading, isError } = useCourseQuery(courseId)
  const { data: enrollments } = useEnrollmentsQuery()
  const [enroll, { isLoading: enrolling }] = useEnrollMutation()
  const [gate, setGate] = useState(false)

  if (isLoading) return <Skeleton className="h-72 w-full rounded-xl" />
  if (isError || !course) {
    return (
      <EmptyState
        title="Курс не найден"
        description="Возможно, он ещё не опубликован."
        mood="sad"
        action={
          <Link to="/catalog">
            <Button variant="secondary">В каталог</Button>
          </Link>
        }
      />
    )
  }

  const enrolled = enrollments?.some((e) => e.course_id === courseId)
  const free = Number(course.price) === 0

  async function handleEnroll() {
    try {
      await enroll(courseId).unwrap()
      notify.success('Вы записаны на курс!')
      nav(`/learn/${courseId}`)
    } catch (e) {
      if ((e as { status?: number }).status === 403) setGate(true)
      else notify.error('Не удалось записаться на курс')
    }
  }

  return (
    <div className="space-y-6">
      <Card>
        <div className="flex flex-wrap items-center gap-2">
          <Badge tone="brand">{TRACK_LABEL[course.track] ?? course.track}</Badge>
          <Badge tone="muted">{LEVEL_LABEL[course.level] ?? course.level}</Badge>
          <Badge tone="muted">
            {course.age_min}–{course.age_max} лет
          </Badge>
          <Badge tone={free ? 'success' : 'sun'}>{free ? 'Бесплатно' : formatMoney(course.price)}</Badge>
        </div>
        <h1 className="mt-3 text-2xl font-extrabold text-ink">{course.title}</h1>
        {course.description && <p className="mt-1 text-muted">{course.description}</p>}
        <p className="mt-3 text-sm text-hint">
          {course.module_count} модулей · {course.lesson_count} уроков
        </p>
        <div className="mt-4">
          {enrolled ? (
            <Link to={`/learn/${courseId}`}>
              <Button>Продолжить обучение</Button>
            </Link>
          ) : (
            <Button onClick={handleEnroll} loading={enrolling}>
              Записаться на курс
            </Button>
          )}
        </div>
      </Card>

      <section className="space-y-4">
        <h2 className="text-lg font-extrabold text-ink">Программа курса</h2>
        {course.modules.map((m, mi) => (
          <Card key={m.id}>
            <h3 className="mb-2 font-extrabold text-ink">
              Модуль {mi + 1}. {m.title}
            </h3>
            <ul className="divide-y divide-line">
              {m.lessons.map((l) => (
                <li key={l.id} className="flex items-center gap-3 py-2.5 text-ink">
                  <BookOpen className="h-4 w-4 text-brand" aria-hidden />
                  <span className="flex-1">{l.title}</span>
                  {l.assignment_count > 0 && (
                    <span className="text-xs text-hint">{l.assignment_count} зад.</span>
                  )}
                </li>
              ))}
            </ul>
          </Card>
        ))}
      </section>

      <Modal open={gate} onOpenChange={setGate} title="Нужен абонемент">
        <div className="flex flex-col items-center gap-3 text-center">
          <Kodik mood="sad" size={96} aria-hidden />
          <p className="text-muted">
            Этот курс платный. Попроси родителя оформить абонемент в разделе «Оплата» — и курс откроется!
          </p>
          <Button onClick={() => setGate(false)}>Понятно</Button>
        </div>
      </Modal>
    </div>
  )
}

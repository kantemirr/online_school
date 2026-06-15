import { Link } from 'react-router-dom'

import { Badge, Card } from '../../components/ui'
import { formatMoney } from '../../lib/format'
import { LEVEL_LABEL, TRACK_LABEL } from '../../lib/labels'
import type { CourseSummary } from './api'

export function CourseCard({ course }: { course: CourseSummary }) {
  const free = Number(course.price) === 0
  return (
    <Link to={`/courses/${course.id}`} className="block h-full">
      <Card className="flex h-full flex-col transition hover:-translate-y-0.5 hover:shadow-pop">
        <div className="flex items-start justify-between gap-2">
          <Badge tone="brand">{TRACK_LABEL[course.track] ?? course.track}</Badge>
          <Badge tone={free ? 'success' : 'sun'}>{free ? 'Бесплатно' : formatMoney(course.price)}</Badge>
        </div>
        <h3 className="mt-3 text-lg font-extrabold text-ink">{course.title}</h3>
        {course.description && (
          <p className="mt-1 line-clamp-2 text-sm text-muted">{course.description}</p>
        )}
        <p className="mt-auto pt-3 text-xs text-hint">
          {course.age_min}–{course.age_max} лет · {LEVEL_LABEL[course.level] ?? course.level}
        </p>
      </Card>
    </Link>
  )
}

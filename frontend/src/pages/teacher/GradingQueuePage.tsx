import { useState } from 'react'

import { ExternalLink } from 'lucide-react'

import { Button, Card, EmptyState, Skeleton } from '../../components/ui'
import { ReviewForm } from '../../features/grading/ReviewForm'
import { useGradingQueueQuery, type QueueItem } from '../../features/grading/api'
import { formatDateTime } from '../../lib/format'

export function GradingQueuePage() {
  const { data, isLoading } = useGradingQueueQuery()
  const [review, setReview] = useState<QueueItem | null>(null)

  if (isLoading) return <Skeleton className="h-60 w-full rounded-xl" />
  if (!data || data.length === 0) {
    return <EmptyState title="Все работы проверены!" description="Очередь проверки пуста." mood="happy" />
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-extrabold text-ink">Очередь проверки</h1>
      <div className="space-y-3">
        {data.map((item) => {
          const isLink = !!item.file_url && /^https?:\/\//.test(item.file_url)
          return (
            <Card key={item.submission_id} className="flex flex-wrap items-center gap-3">
              <div className="flex-1">
                <div className="font-bold text-ink">{item.assignment_title}</div>
                <div className="text-xs text-hint">
                  {item.nickname ?? `ученик #${item.student_id}`} · {formatDateTime(item.created_at)}
                </div>
              </div>
              {isLink ? (
                <a href={item.file_url!} target="_blank" rel="noreferrer">
                  <Button variant="ghost" size="sm">
                    <ExternalLink className="h-4 w-4" aria-hidden /> Работа
                  </Button>
                </a>
              ) : item.file_url ? (
                <span className="text-xs text-hint">файл загружен</span>
              ) : null}
              <Button size="sm" onClick={() => setReview(item)}>
                Проверить
              </Button>
            </Card>
          )
        })}
      </div>
      <ReviewForm item={review} onClose={() => setReview(null)} />
    </div>
  )
}

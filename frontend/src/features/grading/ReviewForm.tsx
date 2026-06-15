import { useState } from 'react'

import { Button, Field, Input, Modal } from '../../components/ui'
import { cn } from '../../lib/cn'
import { notify } from '../../lib/toast'
import { useReviewSubmissionMutation, type QueueItem } from './api'

export function ReviewForm({ item, onClose }: { item: QueueItem | null; onClose: () => void }) {
  const [score, setScore] = useState('80')
  const [feedback, setFeedback] = useState('')
  const [status, setStatus] = useState<'reviewed' | 'needs_revision'>('reviewed')
  const [review, { isLoading }] = useReviewSubmissionMutation()

  async function submit() {
    if (!item) return
    try {
      await review({
        id: item.submission_id,
        score: Number(score),
        feedback: feedback.trim() || undefined,
        status,
      }).unwrap()
      notify.success('Работа проверена')
      onClose()
    } catch {
      notify.error('Не удалось сохранить ревью')
    }
  }

  return (
    <Modal open={!!item} onOpenChange={(o) => !o && onClose()} title={item ? `Проверка: ${item.assignment_title}` : ''}>
      <div className="space-y-4">
        <Field label="Балл (0–100)">
          <Input type="number" min={0} max={100} value={score} onChange={(e) => setScore(e.target.value)} />
        </Field>
        <Field label="Отзыв">
          <textarea
            className="w-full rounded-md border-2 border-line p-2 text-base"
            rows={3}
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
            placeholder="Что получилось хорошо, что улучшить"
          />
        </Field>
        <div className="flex gap-2">
          <button
            onClick={() => setStatus('reviewed')}
            className={cn('flex-1 rounded-md py-2 font-bold transition', status === 'reviewed' ? 'bg-success text-white' : 'bg-cloud text-muted')}
          >
            Принять
          </button>
          <button
            onClick={() => setStatus('needs_revision')}
            className={cn('flex-1 rounded-md py-2 font-bold transition', status === 'needs_revision' ? 'bg-sun text-sun-ink' : 'bg-cloud text-muted')}
          >
            На доработку
          </button>
        </div>
        <Button fullWidth loading={isLoading} onClick={submit}>
          Сохранить
        </Button>
      </div>
    </Modal>
  )
}

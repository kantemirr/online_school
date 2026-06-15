import { useState } from 'react'

import { Kodik } from '../../components/mascot/Kodik'
import { Button, Card, Field, Input } from '../../components/ui'
import { notify } from '../../lib/toast'
import { useSubmitProjectMutation, type AssignmentForSolve } from './api'

export function ProjectUpload({ assignment }: { assignment: AssignmentForSolve }) {
  const [file, setFile] = useState<File | null>(null)
  const [link, setLink] = useState('')
  const [sent, setSent] = useState(false)
  const [submit, { isLoading }] = useSubmitProjectMutation()

  async function onSubmit() {
    const form = new FormData()
    if (file) form.append('file', file)
    if (link.trim()) form.append('link', link.trim())
    try {
      await submit({ id: assignment.id, form }).unwrap()
      setSent(true)
    } catch {
      notify.error('Не удалось отправить проект')
    }
  }

  if (sent) {
    return (
      <Card className="flex flex-col items-center gap-3 text-center">
        <Kodik mood="happy" size={88} aria-hidden />
        <h3 className="text-xl font-extrabold text-ink">Проект отправлен!</h3>
        <p className="text-muted">Преподаватель проверит работу и оставит отзыв с баллами.</p>
      </Card>
    )
  }

  return (
    <Card className="space-y-4">
      <Field label="Файл проекта">
        <input
          type="file"
          onChange={(e) => setFile(e.target.files?.[0] ?? null)}
          className="block w-full text-sm text-muted file:mr-3 file:rounded-md file:border-0 file:bg-brand-50 file:px-3 file:py-2 file:font-bold file:text-brand-700"
        />
      </Field>
      <Field label="Или ссылка (Scratch, GitHub, диск…)">
        <Input placeholder="https://…" value={link} onChange={(e) => setLink(e.target.value)} />
      </Field>
      <Button onClick={onSubmit} loading={isLoading} disabled={!file && !link.trim()}>
        Отправить на проверку
      </Button>
    </Card>
  )
}

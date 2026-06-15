import { useState } from 'react'

import { Button, Field, Input, Modal } from '../../components/ui'
import { notify } from '../../lib/toast'
import { useCreateSessionMutation } from './api'

interface SessionFormProps {
  open: boolean
  onOpenChange: (o: boolean) => void
  groupId: number
}

export function SessionForm({ open, onOpenChange, groupId }: SessionFormProps) {
  const [start, setStart] = useState('')
  const [end, setEnd] = useState('')
  const [url, setUrl] = useState('')
  const [create, { isLoading }] = useCreateSessionMutation()

  async function submit() {
    if (!start || !end) return
    if (new Date(end) <= new Date(start)) {
      notify.error('Окончание должно быть позже начала')
      return
    }
    try {
      await create({
        group_id: groupId,
        starts_at: new Date(start).toISOString(),
        ends_at: new Date(end).toISOString(),
        meeting_url: url.trim() || undefined,
      }).unwrap()
      notify.success('Занятие добавлено')
      onOpenChange(false)
      setStart('')
      setEnd('')
      setUrl('')
    } catch {
      notify.error('Не удалось создать занятие')
    }
  }

  return (
    <Modal open={open} onOpenChange={onOpenChange} title="Новое занятие">
      <div className="space-y-4">
        <Field label="Начало">
          <Input type="datetime-local" value={start} onChange={(e) => setStart(e.target.value)} />
        </Field>
        <Field label="Окончание">
          <Input type="datetime-local" value={end} onChange={(e) => setEnd(e.target.value)} />
        </Field>
        <Field label="Ссылка на видеоконференцию (необязательно)">
          <Input value={url} onChange={(e) => setUrl(e.target.value)} placeholder="https://meet.jit.si/…" />
        </Field>
        <Button fullWidth loading={isLoading} disabled={!start || !end} onClick={submit}>
          Создать занятие
        </Button>
      </div>
    </Modal>
  )
}

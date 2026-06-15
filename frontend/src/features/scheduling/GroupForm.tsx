import { useState } from 'react'

import { Button, Field, Input, Modal } from '../../components/ui'
import { notify } from '../../lib/toast'
import { useCoursesQuery } from '../catalog/api'
import { useCreateGroupMutation } from './api'

export function GroupForm({ open, onOpenChange }: { open: boolean; onOpenChange: (o: boolean) => void }) {
  const { data: courses } = useCoursesQuery({ size: 100 })
  const [createGroup, { isLoading }] = useCreateGroupMutation()
  const [name, setName] = useState('')
  const [courseId, setCourseId] = useState<number | undefined>()

  async function submit() {
    if (!name.trim() || !courseId) return
    try {
      await createGroup({ course_id: courseId, name: name.trim() }).unwrap()
      notify.success('Группа создана')
      onOpenChange(false)
      setName('')
      setCourseId(undefined)
    } catch {
      notify.error('Не удалось создать группу')
    }
  }

  return (
    <Modal open={open} onOpenChange={onOpenChange} title="Новая группа">
      <div className="space-y-4">
        <Field label="Курс">
          <select
            className="w-full rounded-md border-2 border-line px-3 py-2"
            value={courseId ?? ''}
            onChange={(e) => setCourseId(e.target.value ? Number(e.target.value) : undefined)}
          >
            <option value="">— выбери курс —</option>
            {courses?.items.map((c) => (
              <option key={c.id} value={c.id}>
                {c.title}
              </option>
            ))}
          </select>
        </Field>
        <Field label="Название группы">
          <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Питон-понедельник" />
        </Field>
        <Button fullWidth loading={isLoading} disabled={!name.trim() || !courseId} onClick={submit}>
          Создать
        </Button>
      </div>
    </Modal>
  )
}

import { useEffect, useState } from 'react'

import { Button, Field, Input, Modal } from '../../../components/ui'
import { LEVEL_LABEL, TRACK_LABEL } from '../../../lib/labels'
import { notify } from '../../../lib/toast'
import { useCreateCourseMutation, useUpdateCourseMutation, type CourseAdmin } from '../api'

const TRACKS = ['scratch', 'python', 'web', 'gamedev', 'algorithms']
const LEVELS = ['beginner', 'intermediate', 'advanced']

interface CourseFormProps {
  open: boolean
  onOpenChange: (o: boolean) => void
  course?: CourseAdmin
}

export function CourseForm({ open, onOpenChange, course }: CourseFormProps) {
  const editing = !!course
  const [create, { isLoading: creating }] = useCreateCourseMutation()
  const [update, { isLoading: updating }] = useUpdateCourseMutation()
  const [form, setForm] = useState({
    title: '',
    description: '',
    track: 'python',
    age_min: 8,
    age_max: 14,
    level: 'beginner',
    price: '0',
  })
  const set = (k: string, v: string | number) => setForm((f) => ({ ...f, [k]: v }))

  useEffect(() => {
    if (open && course) {
      setForm({
        title: course.title,
        description: course.description ?? '',
        track: course.track,
        age_min: course.age_min,
        age_max: course.age_max,
        level: course.level,
        price: String(course.price),
      })
    } else if (open) {
      setForm({ title: '', description: '', track: 'python', age_min: 8, age_max: 14, level: 'beginner', price: '0' })
    }
  }, [open, course])

  async function submit() {
    if (!form.title.trim()) {
      notify.error('Укажите название')
      return
    }
    const body = {
      title: form.title,
      description: form.description || null,
      track: form.track,
      age_min: Number(form.age_min),
      age_max: Number(form.age_max),
      level: form.level,
      price: form.price,
    }
    try {
      if (editing) await update({ id: course!.id, ...body }).unwrap()
      else await create(body).unwrap()
      notify.success(editing ? 'Курс обновлён' : 'Курс создан')
      onOpenChange(false)
    } catch {
      notify.error('Не удалось сохранить курс')
    }
  }

  return (
    <Modal open={open} onOpenChange={onOpenChange} title={editing ? 'Изменить курс' : 'Новый курс'}>
      <div className="space-y-4">
        <Field label="Название">
          <Input value={form.title} onChange={(e) => set('title', e.target.value)} />
        </Field>
        <Field label="Описание">
          <textarea className="w-full rounded-md border-2 border-line p-2 text-base" rows={2} value={form.description} onChange={(e) => set('description', e.target.value)} />
        </Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Направление">
            <select className="w-full rounded-md border-2 border-line px-3 py-2" value={form.track} onChange={(e) => set('track', e.target.value)}>
              {TRACKS.map((t) => <option key={t} value={t}>{TRACK_LABEL[t]}</option>)}
            </select>
          </Field>
          <Field label="Уровень">
            <select className="w-full rounded-md border-2 border-line px-3 py-2" value={form.level} onChange={(e) => set('level', e.target.value)}>
              {LEVELS.map((l) => <option key={l} value={l}>{LEVEL_LABEL[l]}</option>)}
            </select>
          </Field>
          <Field label="Возраст от">
            <Input type="number" value={form.age_min} onChange={(e) => set('age_min', e.target.value)} />
          </Field>
          <Field label="Возраст до">
            <Input type="number" value={form.age_max} onChange={(e) => set('age_max', e.target.value)} />
          </Field>
        </div>
        <Field label="Цена, ₽ (0 — бесплатно)">
          <Input type="number" value={form.price} onChange={(e) => set('price', e.target.value)} />
        </Field>
        <Button fullWidth loading={creating || updating} onClick={submit}>
          {editing ? 'Сохранить' : 'Создать курс'}
        </Button>
      </div>
    </Modal>
  )
}

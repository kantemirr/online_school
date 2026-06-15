import { useState } from 'react'

import { Button, Field, Input, Modal } from '../../components/ui'
import { notify } from '../../lib/toast'
import { useCreateStaffMutation } from './api'

const EMPTY = { email: '', password: '', role: 'teacher', full_name: '', specialization: '' }

export function StaffForm({ open, onOpenChange }: { open: boolean; onOpenChange: (o: boolean) => void }) {
  const [createStaff, { isLoading }] = useCreateStaffMutation()
  const [form, setForm] = useState(EMPTY)
  const set = (k: keyof typeof EMPTY, v: string) => setForm((f) => ({ ...f, [k]: v }))

  async function submit() {
    if (!form.email || form.password.length < 8 || !form.full_name) {
      notify.error('Заполните email, имя и пароль (от 8 символов)')
      return
    }
    try {
      await createStaff({
        email: form.email,
        password: form.password,
        role: form.role,
        full_name: form.full_name,
        specialization: form.specialization || undefined,
      }).unwrap()
      notify.success('Сотрудник создан')
      onOpenChange(false)
      setForm(EMPTY)
    } catch (e) {
      notify.error((e as { data?: { error?: { message?: string } } })?.data?.error?.message ?? 'Не удалось создать')
    }
  }

  return (
    <Modal open={open} onOpenChange={onOpenChange} title="Создать сотрудника">
      <div className="space-y-4">
        <Field label="Email">
          <Input type="email" value={form.email} onChange={(e) => set('email', e.target.value)} />
        </Field>
        <Field label="Пароль (от 8 символов)">
          <Input type="password" value={form.password} onChange={(e) => set('password', e.target.value)} />
        </Field>
        <Field label="Роль">
          <select className="w-full rounded-md border-2 border-line px-3 py-2" value={form.role} onChange={(e) => set('role', e.target.value)}>
            <option value="teacher">Преподаватель</option>
            <option value="admin">Администратор</option>
          </select>
        </Field>
        <Field label="Имя и фамилия">
          <Input value={form.full_name} onChange={(e) => set('full_name', e.target.value)} />
        </Field>
        {form.role === 'teacher' && (
          <Field label="Специализация (необязательно)">
            <Input value={form.specialization} onChange={(e) => set('specialization', e.target.value)} placeholder="Python, Scratch…" />
          </Field>
        )}
        <Button fullWidth loading={isLoading} onClick={submit}>
          Создать
        </Button>
      </div>
    </Modal>
  )
}

import { useEffect } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { z } from 'zod'

import { Button, Field, Input, Modal } from '../../components/ui'
import { notify } from '../../lib/toast'
import { useCreateChildMutation, useUpdateChildMutation, type ChildOut } from '../users/api'

const createSchema = z.object({
  nickname: z.string().min(1, 'Укажите ник').max(64),
  birth_date: z.string().min(1, 'Укажите дату рождения'),
  login_username: z.string().min(3, 'Минимум 3 символа').max(64),
  pin: z.string().regex(/^\d{4,6}$/, 'PIN — 4–6 цифр'),
})
const editSchema = z.object({
  nickname: z.string().min(1, 'Укажите ник').max(64),
  pin: z.union([z.string().regex(/^\d{4,6}$/, 'PIN — 4–6 цифр'), z.literal('')]),
})

type Values = {
  nickname: string
  birth_date?: string
  login_username?: string
  pin?: string
}

interface ChildFormProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  child?: ChildOut
}

export function ChildForm({ open, onOpenChange, child }: ChildFormProps) {
  const editing = !!child
  const [createChild] = useCreateChildMutation()
  const [updateChild] = useUpdateChildMutation()

  const {
    register,
    handleSubmit,
    reset,
    setError,
    formState: { errors, isSubmitting },
  } = useForm<Values>({ resolver: zodResolver((editing ? editSchema : createSchema) as never) })

  useEffect(() => {
    if (open) reset(editing ? { nickname: child!.nickname, pin: '' } : { nickname: '', birth_date: '', login_username: '', pin: '' })
  }, [open, editing, child, reset])

  async function onSubmit(values: Values) {
    try {
      if (editing) {
        await updateChild({ id: child!.user_id, nickname: values.nickname, pin: values.pin || undefined }).unwrap()
        notify.success('Профиль обновлён')
      } else {
        await createChild({
          nickname: values.nickname,
          birth_date: values.birth_date!,
          login_username: values.login_username!,
          pin: values.pin!,
        }).unwrap()
        notify.success('Ребёнок добавлен')
      }
      onOpenChange(false)
    } catch (e) {
      const code = (e as { data?: { error?: { code?: string } } })?.data?.error?.code
      if (code === 'username_taken') setError('login_username', { message: 'Логин уже занят' })
      else notify.error('Не удалось сохранить')
    }
  }

  return (
    <Modal open={open} onOpenChange={onOpenChange} title={editing ? 'Изменить профиль' : 'Добавить ребёнка'}>
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Field label="Ник ребёнка" error={errors.nickname?.message}>
          <Input placeholder="CodeStar" {...register('nickname')} />
        </Field>
        {!editing && (
          <>
            <Field label="Дата рождения" error={errors.birth_date?.message}>
              <Input type="date" {...register('birth_date')} />
            </Field>
            <Field label="Логин для входа" error={errors.login_username?.message}>
              <Input placeholder="codestar" autoCapitalize="none" {...register('login_username')} />
            </Field>
          </>
        )}
        <Field label={editing ? 'Новый PIN (необязательно)' : 'PIN-код (4–6 цифр)'} error={errors.pin?.message}>
          <Input inputMode="numeric" maxLength={6} placeholder="••••" {...register('pin')} />
        </Field>
        <Button type="submit" fullWidth loading={isSubmitting}>
          {editing ? 'Сохранить' : 'Добавить'}
        </Button>
      </form>
    </Modal>
  )
}

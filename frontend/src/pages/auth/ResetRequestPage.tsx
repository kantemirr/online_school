import { useState } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { z } from 'zod'

import { AuthLayout } from '../../components/auth/AuthLayout'
import { Button, Field, Input } from '../../components/ui'
import { useResetRequestMutation } from '../../features/auth/api'

const schema = z.object({ email: z.string().email('Неверный email') })
type Values = z.infer<typeof schema>

export function ResetRequestPage() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Values>({ resolver: zodResolver(schema) })
  const [resetRequest] = useResetRequestMutation()
  const [sent, setSent] = useState(false)

  async function onSubmit(values: Values) {
    await resetRequest(values).unwrap().catch(() => undefined)
    setSent(true) // не раскрываем, существует ли аккаунт
  }

  if (sent) {
    return (
      <AuthLayout title="Проверьте почту" subtitle="Если аккаунт существует — письмо отправлено" mood="happy">
        <Link to="/login">
          <Button fullWidth>Ко входу</Button>
        </Link>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout
      title="Восстановление пароля"
      subtitle="Введите email — пришлём ссылку"
      mood="thinking"
      footer={
        <Link to="/login" className="font-bold text-brand">
          Вспомнил пароль
        </Link>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Field label="Email" error={errors.email?.message}>
          <Input type="email" placeholder="parent@mail.ru" {...register('email')} />
        </Field>
        <Button type="submit" fullWidth loading={isSubmitting}>
          Отправить ссылку
        </Button>
      </form>
    </AuthLayout>
  )
}

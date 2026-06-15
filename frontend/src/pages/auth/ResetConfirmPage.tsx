import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link, useNavigate, useSearchParams } from 'react-router-dom'
import { z } from 'zod'

import { AuthLayout } from '../../components/auth/AuthLayout'
import { Button, Field, Input } from '../../components/ui'
import { useResetConfirmMutation } from '../../features/auth/api'
import { notify } from '../../lib/toast'

const schema = z.object({ new_password: z.string().min(8, 'Минимум 8 символов') })
type Values = z.infer<typeof schema>

export function ResetConfirmPage() {
  const [params] = useSearchParams()
  const token = params.get('token')
  const [resetConfirm] = useResetConfirmMutation()
  const nav = useNavigate()
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Values>({ resolver: zodResolver(schema) })

  async function onSubmit(values: Values) {
    if (!token) {
      notify.error('Ссылка недействительна')
      return
    }
    try {
      await resetConfirm({ token, new_password: values.new_password }).unwrap()
      notify.success('Пароль обновлён — войдите заново')
      nav('/login', { replace: true })
    } catch {
      notify.error('Ссылка устарела или недействительна')
    }
  }

  return (
    <AuthLayout
      title="Новый пароль"
      subtitle="Придумайте надёжный пароль"
      footer={
        <Link to="/login" className="font-bold text-brand">
          Ко входу
        </Link>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Field label="Новый пароль" error={errors.new_password?.message}>
          <Input type="password" placeholder="минимум 8 символов" {...register('new_password')} />
        </Field>
        <Button type="submit" fullWidth loading={isSubmitting}>
          Сохранить пароль
        </Button>
      </form>
    </AuthLayout>
  )
}

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { AuthLayout } from '../../components/auth/AuthLayout'
import { Button, Field, Input } from '../../components/ui'
import { useLoginMutation } from '../../features/auth/api'
import { setTokens, setUser } from '../../features/auth/authSlice'
import { useLazyMeQuery } from '../../features/users/api'
import { ROLE_HOME } from '../../lib/roles'
import { notify } from '../../lib/toast'
import { useAppDispatch } from '../../store/hooks'

const schema = z.object({
  email: z.string().email('Неверный email'),
  password: z.string().min(1, 'Введите пароль'),
})
type Values = z.infer<typeof schema>

export function LoginPage() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Values>({ resolver: zodResolver(schema) })
  const [login] = useLoginMutation()
  const [fetchMe] = useLazyMeQuery()
  const dispatch = useAppDispatch()
  const nav = useNavigate()

  async function onSubmit(values: Values) {
    try {
      const tokens = await login(values).unwrap()
      dispatch(setTokens({ accessToken: tokens.access_token, refreshToken: tokens.refresh_token }))
      const me = await fetchMe().unwrap()
      dispatch(setUser({ id: me.id, email: me.email, role: me.role, display_name: me.display_name }))
      if (me.role === 'student' && !localStorage.getItem('codekids_onboarded')) {
        nav('/onboarding', { replace: true })
      } else {
        nav(ROLE_HOME[me.role], { replace: true })
      }
    } catch (e) {
      notify.error((e as { data?: { error?: { message?: string } } })?.data?.error?.message ?? 'Не удалось войти')
    }
  }

  return (
    <AuthLayout
      title="С возвращением!"
      subtitle="Вход для родителей и персонала"
      footer={
        <>
          Нет аккаунта?{' '}
          <Link to="/register" className="font-bold text-brand">
            Регистрация
          </Link>{' '}
          ·{' '}
          <Link to="/login/child" className="font-bold text-brand">
            Вход для ребёнка
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Field label="Email" error={errors.email?.message}>
          <Input type="email" placeholder="parent@mail.ru" autoComplete="email" {...register('email')} />
        </Field>
        <Field label="Пароль" error={errors.password?.message}>
          <Input type="password" placeholder="••••••••" autoComplete="current-password" {...register('password')} />
        </Field>
        <div className="text-right">
          <Link to="/reset-password" className="text-sm font-bold text-brand">
            Забыли пароль?
          </Link>
        </div>
        <Button type="submit" fullWidth loading={isSubmitting}>
          Войти
        </Button>
      </form>
    </AuthLayout>
  )
}

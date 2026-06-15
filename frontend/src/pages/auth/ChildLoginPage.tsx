import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from 'react-router-dom'
import { z } from 'zod'

import { AuthLayout } from '../../components/auth/AuthLayout'
import { Button, Field, Input } from '../../components/ui'
import { useChildLoginMutation } from '../../features/auth/api'
import { setTokens, setUser } from '../../features/auth/authSlice'
import { useLazyMeQuery } from '../../features/users/api'
import { notify } from '../../lib/toast'
import { useAppDispatch } from '../../store/hooks'

const schema = z.object({
  login_username: z.string().min(3, 'Минимум 3 символа'),
  pin: z.string().regex(/^\d{4,6}$/, 'PIN — 4–6 цифр'),
})
type Values = z.infer<typeof schema>

export function ChildLoginPage() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Values>({ resolver: zodResolver(schema) })
  const [childLogin] = useChildLoginMutation()
  const [fetchMe] = useLazyMeQuery()
  const dispatch = useAppDispatch()
  const nav = useNavigate()

  async function onSubmit(values: Values) {
    try {
      const tokens = await childLogin(values).unwrap()
      dispatch(setTokens({ accessToken: tokens.access_token, refreshToken: tokens.refresh_token }))
      const me = await fetchMe().unwrap()
      dispatch(setUser({ id: me.id, email: me.email, role: me.role, display_name: me.display_name }))
      if (!localStorage.getItem('codekids_onboarded')) {
        nav('/onboarding', { replace: true })
      } else {
        nav('/home', { replace: true })
      }
    } catch {
      notify.error('Неверный логин или PIN')
    }
  }

  return (
    <AuthLayout
      title="Привет, юный кодер!"
      subtitle="Введи свой логин и PIN"
      mood="happy"
      footer={
        <Link to="/login" className="font-bold text-brand">
          Я родитель
        </Link>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Field label="Логин" error={errors.login_username?.message}>
          <Input placeholder="codestar" autoCapitalize="none" {...register('login_username')} />
        </Field>
        <Field label="PIN-код" error={errors.pin?.message}>
          <Input
            inputMode="numeric"
            maxLength={6}
            placeholder="••••"
            className="text-center text-2xl tracking-[0.5em]"
            {...register('pin')}
          />
        </Field>
        <Button type="submit" variant="reward" fullWidth loading={isSubmitting}>
          Войти
        </Button>
      </form>
    </AuthLayout>
  )
}

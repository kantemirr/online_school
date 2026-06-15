import { useState } from 'react'

import { zodResolver } from '@hookform/resolvers/zod'
import { useForm } from 'react-hook-form'
import { Link } from 'react-router-dom'
import { z } from 'zod'

import { AuthLayout } from '../../components/auth/AuthLayout'
import { Button, Field, Input } from '../../components/ui'
import { useRegisterMutation } from '../../features/auth/api'
import { notify } from '../../lib/toast'

const schema = z.object({
  full_name: z.string().min(1, 'Укажите имя'),
  email: z.string().email('Неверный email'),
  phone: z.string().max(32).optional().or(z.literal('')),
  password: z.string().min(8, 'Минимум 8 символов'),
  consent_pdn: z.literal(true, { errorMap: () => ({ message: 'Нужно согласие на обработку данных' }) }),
})
type Values = z.infer<typeof schema>

export function RegisterPage() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<Values>({ resolver: zodResolver(schema) })
  const [doRegister] = useRegisterMutation()
  const [done, setDone] = useState(false)

  async function onSubmit(values: Values) {
    try {
      await doRegister({
        full_name: values.full_name,
        email: values.email,
        phone: values.phone || undefined,
        password: values.password,
        consent_pdn: true,
      }).unwrap()
      setDone(true)
    } catch (e) {
      notify.error((e as { data?: { error?: { message?: string } } })?.data?.error?.message ?? 'Не удалось зарегистрироваться')
    }
  }

  if (done) {
    return (
      <AuthLayout title="Почти готово!" subtitle="Подтвердите email" mood="happy">
        <p className="text-center text-muted">
          Мы отправили письмо со ссылкой подтверждения. Откройте его (в демо — MailHog на :8025), затем войдите.
        </p>
        <Link to="/login" className="mt-4 block">
          <Button fullWidth>Перейти ко входу</Button>
        </Link>
      </AuthLayout>
    )
  }

  return (
    <AuthLayout
      title="Регистрация родителя"
      subtitle="Заведите аккаунт и добавьте ребёнка"
      footer={
        <>
          Уже есть аккаунт?{' '}
          <Link to="/login" className="font-bold text-brand">
            Войти
          </Link>
        </>
      }
    >
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
        <Field label="Имя и фамилия" error={errors.full_name?.message}>
          <Input placeholder="Анна Кодова" {...register('full_name')} />
        </Field>
        <Field label="Email" error={errors.email?.message}>
          <Input type="email" placeholder="parent@mail.ru" {...register('email')} />
        </Field>
        <Field label="Телефон (необязательно)" error={errors.phone?.message}>
          <Input placeholder="+7 900 000-00-00" {...register('phone')} />
        </Field>
        <Field label="Пароль" error={errors.password?.message}>
          <Input type="password" placeholder="минимум 8 символов" {...register('password')} />
        </Field>
        <label className="flex items-start gap-2 text-sm text-muted">
          <input type="checkbox" className="mt-1 h-4 w-4 accent-brand" {...register('consent_pdn')} />
          <span>
            Согласен на обработку персональных данных (в т.ч. ребёнка) согласно ФЗ-152.
            {errors.consent_pdn && (
              <span className="mt-1 block font-bold text-danger-700">{errors.consent_pdn.message}</span>
            )}
          </span>
        </label>
        <Button type="submit" fullWidth loading={isSubmitting}>
          Зарегистрироваться
        </Button>
      </form>
    </AuthLayout>
  )
}

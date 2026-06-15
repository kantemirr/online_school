import { useState } from 'react'

import { LogOut } from 'lucide-react'
import { useNavigate } from 'react-router-dom'

import { Avatar, Badge, Button, Card, Field, Input } from '../components/ui'
import { useChangePasswordMutation, useLogoutMutation } from '../features/auth/api'
import { logout, setTokens } from '../features/auth/authSlice'
import { ROLE_LABEL } from '../lib/roles'
import { notify } from '../lib/toast'
import { useAppDispatch, useAppSelector } from '../store/hooks'

export function ProfilePage() {
  const user = useAppSelector((s) => s.auth.user)
  const refreshToken = useAppSelector((s) => s.auth.refreshToken)
  const dispatch = useAppDispatch()
  const nav = useNavigate()
  const [changePassword, { isLoading }] = useChangePasswordMutation()
  const [doLogout] = useLogoutMutation()
  const [oldP, setOldP] = useState('')
  const [newP, setNewP] = useState('')

  if (!user) return null
  const isStaff = user.role !== 'student'

  async function submitPwd() {
    if (newP.length < 8) {
      notify.error('Новый пароль — минимум 8 символов')
      return
    }
    try {
      const pair = await changePassword({ old_password: oldP, new_password: newP }).unwrap()
      dispatch(setTokens({ accessToken: pair.access_token, refreshToken: pair.refresh_token }))
      notify.success('Пароль изменён')
      setOldP('')
      setNewP('')
    } catch (e) {
      notify.error((e as { data?: { error?: { message?: string } } })?.data?.error?.message ?? 'Не удалось сменить пароль')
    }
  }

  async function handleLogout() {
    if (refreshToken) {
      await doLogout({ refresh_token: refreshToken }).unwrap().catch(() => undefined)
    }
    dispatch(logout())
    nav('/login', { replace: true })
  }

  return (
    <div className="mx-auto max-w-lg space-y-6">
      <h1 className="text-2xl font-extrabold text-ink">Мой профиль</h1>

      <Card className="flex items-center gap-4">
        <Avatar name={user.display_name ?? user.email ?? 'CodeKids'} size={56} />
        <div className="min-w-0">
          <div className="truncate text-lg font-extrabold text-ink">{user.display_name ?? 'Без имени'}</div>
          {user.email && <div className="truncate text-sm text-muted">{user.email}</div>}
          <Badge tone="brand" className="mt-1">{ROLE_LABEL[user.role]}</Badge>
        </div>
      </Card>

      {isStaff && (
        <Card className="space-y-4">
          <h2 className="text-lg font-extrabold text-ink">Смена пароля</h2>
          <Field label="Текущий пароль">
            <Input type="password" value={oldP} onChange={(e) => setOldP(e.target.value)} />
          </Field>
          <Field label="Новый пароль (от 8 символов)">
            <Input type="password" value={newP} onChange={(e) => setNewP(e.target.value)} />
          </Field>
          <Button loading={isLoading} disabled={!oldP || !newP} onClick={submitPwd}>
            Изменить пароль
          </Button>
        </Card>
      )}

      <Button variant="danger" fullWidth onClick={handleLogout}>
        <LogOut className="h-4 w-4" aria-hidden /> Выйти из аккаунта
      </Button>
    </div>
  )
}

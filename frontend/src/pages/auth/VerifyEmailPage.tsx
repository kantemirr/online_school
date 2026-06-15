import { useEffect, useRef, useState } from 'react'

import { Link, useSearchParams } from 'react-router-dom'

import { AuthLayout } from '../../components/auth/AuthLayout'
import { Button } from '../../components/ui'
import { useVerifyEmailMutation } from '../../features/auth/api'

export function VerifyEmailPage() {
  const [params] = useSearchParams()
  const token = params.get('token')
  const [verify] = useVerifyEmailMutation()
  const [state, setState] = useState<'loading' | 'ok' | 'fail'>('loading')
  const ran = useRef(false)

  useEffect(() => {
    if (ran.current) return
    ran.current = true
    if (!token) {
      setState('fail')
      return
    }
    verify({ token })
      .unwrap()
      .then(() => setState('ok'))
      .catch(() => setState('fail'))
  }, [token, verify])

  if (state === 'loading') {
    return <AuthLayout title="Проверяем ссылку…" mood="thinking" children={<p className="text-center text-muted">Секундочку…</p>} />
  }
  if (state === 'ok') {
    return (
      <AuthLayout title="Email подтверждён!" subtitle="Теперь можно войти" mood="celebrate">
        <Link to="/login">
          <Button fullWidth>Войти</Button>
        </Link>
      </AuthLayout>
    )
  }
  return (
    <AuthLayout title="Ссылка недействительна" subtitle="Возможно, она устарела" mood="sad">
      <Link to="/login">
        <Button fullWidth variant="secondary">
          Вернуться ко входу
        </Button>
      </Link>
    </AuthLayout>
  )
}

import { useState } from 'react'

import { Button, Field, Input, Modal } from '../../components/ui'
import { notify } from '../../lib/toast'
import { useResetPasswordMutation } from './api'

export function ResetPasswordModal({ userId, onClose }: { userId: number | null; onClose: () => void }) {
  const [pwd, setPwd] = useState('')
  const [reset, { isLoading }] = useResetPasswordMutation()

  async function submit() {
    if (pwd.length < 8) {
      notify.error('Минимум 8 символов')
      return
    }
    if (userId == null) return
    try {
      await reset({ id: userId, new_password: pwd }).unwrap()
      notify.success('Пароль сброшен')
      setPwd('')
      onClose()
    } catch {
      notify.error('Не удалось сбросить пароль')
    }
  }

  return (
    <Modal open={userId != null} onOpenChange={(o) => !o && onClose()} title="Сбросить пароль">
      <div className="space-y-4">
        <Field label="Новый пароль">
          <Input type="password" value={pwd} onChange={(e) => setPwd(e.target.value)} placeholder="от 8 символов" />
        </Field>
        <Button fullWidth loading={isLoading} onClick={submit}>
          Сбросить
        </Button>
      </div>
    </Modal>
  )
}

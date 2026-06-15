import { useEffect, useState } from 'react'

import { Search, UserPlus } from 'lucide-react'

import { Button, Input, Modal } from '../../components/ui'
import { notify } from '../../lib/toast'
import { useAddMemberMutation, useLazySearchStudentsQuery } from './api'

interface StudentPickerProps {
  open: boolean
  onOpenChange: (o: boolean) => void
  groupId: number
}

export function StudentPicker({ open, onOpenChange, groupId }: StudentPickerProps) {
  const [q, setQ] = useState('')
  const [search, { data, isFetching }] = useLazySearchStudentsQuery()
  const [addMember] = useAddMemberMutation()

  useEffect(() => {
    if (open) search('')
  }, [open, search])

  async function add(studentId: number) {
    try {
      await addMember({ group_id: groupId, student_id: studentId }).unwrap()
      notify.success('Ученик добавлен в группу')
      onOpenChange(false)
    } catch {
      notify.error('Не удалось добавить (возможно, уже в группе)')
    }
  }

  return (
    <Modal open={open} onOpenChange={onOpenChange} title="Добавить ученика">
      <div className="space-y-3">
        <div className="flex gap-2">
          <Input
            value={q}
            onChange={(e) => setQ(e.target.value)}
            placeholder="Имя или логин ученика"
            onKeyDown={(e) => e.key === 'Enter' && search(q)}
          />
          <Button onClick={() => search(q)} loading={isFetching} aria-label="Искать">
            <Search className="h-4 w-4" aria-hidden />
          </Button>
        </div>
        <ul className="max-h-64 space-y-1 overflow-y-auto">
          {data?.map((s) => (
            <li key={s.student_id} className="flex items-center gap-2 rounded-md border border-line p-2">
              <span className="flex-1">
                <span className="font-bold text-ink">{s.nickname}</span>{' '}
                <span className="text-xs text-hint">{s.login_username}</span>
              </span>
              <Button size="sm" variant="secondary" onClick={() => add(s.student_id)} aria-label="Добавить">
                <UserPlus className="h-4 w-4" aria-hidden />
              </Button>
            </li>
          ))}
          {data && data.length === 0 && <li className="text-sm text-hint">Никого не найдено</li>}
        </ul>
      </div>
    </Modal>
  )
}

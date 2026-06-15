import { useState } from 'react'

import { KeyRound, Search, UserPlus } from 'lucide-react'

import { Badge, Button, Card, Input, Skeleton } from '../../components/ui'
import { ResetPasswordModal } from '../../features/admin/ResetPasswordModal'
import { StaffForm } from '../../features/admin/StaffForm'
import { useAdminUsersQuery, useUpdateUserMutation, type AdminUser } from '../../features/admin/api'
import { cn } from '../../lib/cn'
import { formatDate } from '../../lib/format'
import { ROLE_LABEL } from '../../lib/roles'
import { notify } from '../../lib/toast'
import { useDebounced } from '../../lib/useDebounced'

const ROLES = ['student', 'parent', 'teacher', 'admin']
const ROLE_TONE: Record<string, 'brand' | 'teal' | 'sun' | 'coral'> = {
  student: 'brand',
  parent: 'teal',
  teacher: 'sun',
  admin: 'coral',
}
const SIZE = 20

export function AdminUsersPage() {
  const [role, setRole] = useState<string | undefined>()
  const [rawQ, setRawQ] = useState('')
  const [page, setPage] = useState(1)
  const [staffOpen, setStaffOpen] = useState(false)
  const [resetId, setResetId] = useState<number | null>(null)
  const q = useDebounced(rawQ)

  const { data, isFetching } = useAdminUsersQuery({ role, q: q || undefined, page, size: SIZE })
  const [updateUser] = useUpdateUserMutation()
  const totalPages = data ? Math.max(1, Math.ceil(data.total / SIZE)) : 1

  async function patch(u: AdminUser, body: { is_active?: boolean; role?: string }) {
    try {
      await updateUser({ id: u.id, ...body }).unwrap()
      notify.success('Готово')
    } catch (e) {
      notify.error((e as { data?: { error?: { message?: string } } })?.data?.error?.message ?? 'Не удалось изменить')
    }
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-extrabold text-ink">Пользователи</h1>
        <Button onClick={() => setStaffOpen(true)}>
          <UserPlus className="h-4 w-4" aria-hidden /> Создать сотрудника
        </Button>
      </div>

      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-hint" aria-hidden />
        <Input className="pl-10" placeholder="Поиск по email или имени…" value={rawQ} onChange={(e) => { setRawQ(e.target.value); setPage(1) }} />
      </div>

      <div className="flex flex-wrap gap-2">
        <Chip active={!role} onClick={() => { setRole(undefined); setPage(1) }}>Все роли</Chip>
        {ROLES.map((r) => (
          <Chip key={r} active={role === r} onClick={() => { setRole(r); setPage(1) }}>
            {ROLE_LABEL[r as keyof typeof ROLE_LABEL]}
          </Chip>
        ))}
      </div>

      {isFetching && !data ? (
        <Skeleton className="h-72 w-full rounded-xl" />
      ) : !data || data.items.length === 0 ? (
        <Card className="text-muted">Никого не найдено.</Card>
      ) : (
        <Card className="p-0">
          <ul className="divide-y divide-line">
            {data.items.map((u) => (
              <li key={u.id} className="flex flex-wrap items-center gap-3 px-4 py-3">
                <div className="min-w-0 flex-1">
                  <div className="truncate font-bold text-ink">{u.display_name ?? u.email ?? `#${u.id}`}</div>
                  <div className="truncate text-xs text-hint">{u.email ?? 'без email'} · {formatDate(u.created_at)}</div>
                </div>
                <Badge tone={ROLE_TONE[u.role]}>{ROLE_LABEL[u.role]}</Badge>
                <Badge tone={u.is_active ? 'success' : 'danger'}>{u.is_active ? 'Активен' : 'Заблокирован'}</Badge>
                <div className="flex gap-1">
                  <Button variant="ghost" size="sm" onClick={() => patch(u, { is_active: !u.is_active })}>
                    {u.is_active ? 'Блок' : 'Разблок'}
                  </Button>
                  {(u.role === 'teacher' || u.role === 'admin') && (
                    <Button variant="ghost" size="sm" onClick={() => patch(u, { role: u.role === 'teacher' ? 'admin' : 'teacher' })}>
                      → {u.role === 'teacher' ? 'админ' : 'препод'}
                    </Button>
                  )}
                  <Button variant="ghost" size="sm" aria-label="Сбросить пароль" onClick={() => setResetId(u.id)}>
                    <KeyRound className="h-4 w-4" aria-hidden />
                  </Button>
                </div>
              </li>
            ))}
          </ul>
        </Card>
      )}

      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-3">
          <Button variant="ghost" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>Назад</Button>
          <span className="text-sm font-bold text-muted">{page} / {totalPages}</span>
          <Button variant="ghost" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>Вперёд</Button>
        </div>
      )}

      <StaffForm open={staffOpen} onOpenChange={setStaffOpen} />
      <ResetPasswordModal userId={resetId} onClose={() => setResetId(null)} />
    </div>
  )
}

function Chip({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={cn('rounded-full px-4 py-1.5 text-sm font-bold transition', active ? 'bg-brand text-white' : 'border border-line bg-surface text-muted hover:border-brand-200')}
    >
      {children}
    </button>
  )
}

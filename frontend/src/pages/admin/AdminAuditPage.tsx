import { useState } from 'react'

import { Badge, Button, Card, EmptyState, Skeleton } from '../../components/ui'
import { useAuditQuery } from '../../features/admin/api'
import { formatDateTime } from '../../lib/format'

const ACTION_LABEL: Record<string, string> = {
  user_update: 'Изменение пользователя',
  password_reset: 'Сброс пароля',
  staff_create: 'Создание сотрудника',
}
const SIZE = 50

export function AdminAuditPage() {
  const [page, setPage] = useState(1)
  const { data, isFetching, isError, refetch } = useAuditQuery({ page, size: SIZE })
  const totalPages = data ? Math.max(1, Math.ceil(data.total / SIZE)) : 1

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-extrabold text-ink">Журнал аудита</h1>
      <p className="text-sm text-muted">Ключевые действия администраторов (надёжность и безопасность).</p>

      {isError ? (
        <EmptyState
          title="Не удалось загрузить"
          description="Проверьте соединение и попробуйте ещё раз."
          mood="sad"
          action={<Button variant="secondary" onClick={() => refetch()}>Повторить</Button>}
        />
      ) : isFetching && !data ? (
        <Skeleton className="h-72 w-full rounded-xl" />
      ) : !data || data.items.length === 0 ? (
        <EmptyState title="Журнал пуст" description="Действия администраторов появятся здесь." mood="idle" />
      ) : (
        <Card className="p-0">
          <ul className="divide-y divide-line">
            {data.items.map((a) => (
              <li key={a.id} className="flex flex-wrap items-center gap-3 px-4 py-3">
                <Badge tone="brand">{ACTION_LABEL[a.action] ?? a.action}</Badge>
                <span className="flex-1 text-sm text-ink">
                  {a.actor_email ?? '—'}
                  {a.target && <span className="text-hint"> · {a.target}</span>}
                </span>
                <span className="text-xs text-hint">{formatDateTime(a.created_at)}</span>
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
    </div>
  )
}

import { useState } from 'react'

import { Button, Card, EmptyState, Skeleton } from '../../components/ui'
import { useAdminGroupsQuery } from '../../features/admin/api'

const SIZE = 20

export function AdminGroupsPage() {
  const [page, setPage] = useState(1)
  const { data, isFetching, isError, refetch } = useAdminGroupsQuery({ page, size: SIZE })
  const totalPages = data ? Math.max(1, Math.ceil(data.total / SIZE)) : 1

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-extrabold text-ink">Реестр групп</h1>

      {isError ? (
        <EmptyState
          title="Не удалось загрузить"
          description="Проверьте соединение и попробуйте ещё раз."
          mood="sad"
          action={<Button variant="secondary" onClick={() => refetch()}>Повторить</Button>}
        />
      ) : isFetching && !data ? (
        <Skeleton className="h-60 w-full rounded-xl" />
      ) : !data || data.items.length === 0 ? (
        <EmptyState title="Групп пока нет" description="Группы появятся, когда преподаватели их создадут." mood="idle" />
      ) : (
        <Card className="p-0">
          <ul className="divide-y divide-line">
            {data.items.map((g) => (
              <li key={g.id} className="flex flex-wrap items-center gap-3 px-4 py-3">
                <div className="flex-1">
                  <div className="font-bold text-ink">{g.name}</div>
                  <div className="text-xs text-hint">
                    {g.teacher_name ?? '—'} · {g.course_title ?? '—'}
                  </div>
                </div>
                <span className="text-sm text-muted">
                  {g.members} учеников · {g.sessions} занятий
                </span>
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

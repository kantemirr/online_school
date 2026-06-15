import { useState } from 'react'

import { Badge, Button, Card, EmptyState, Skeleton } from '../../components/ui'
import { useAdminPaymentsQuery } from '../../features/admin/api'
import { cn } from '../../lib/cn'
import { formatDate, formatMoney } from '../../lib/format'
import { PAY_STATUS_LABEL, PLAN_LABEL } from '../../lib/labels'

const STATUSES = ['paid', 'pending', 'failed', 'refunded']
const PAY_TONE: Record<string, 'success' | 'sun' | 'danger' | 'muted'> = {
  paid: 'success',
  pending: 'sun',
  failed: 'danger',
  refunded: 'muted',
}
const SIZE = 20

export function AdminPaymentsPage() {
  const [status, setStatus] = useState<string | undefined>()
  const [page, setPage] = useState(1)
  const { data, isFetching, isError, refetch } = useAdminPaymentsQuery({ status, page, size: SIZE })
  const totalPages = data ? Math.max(1, Math.ceil(data.total / SIZE)) : 1

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-extrabold text-ink">Реестр платежей</h1>

      <div className="flex flex-wrap gap-2">
        <Chip active={!status} onClick={() => { setStatus(undefined); setPage(1) }}>Все</Chip>
        {STATUSES.map((s) => (
          <Chip key={s} active={status === s} onClick={() => { setStatus(s); setPage(1) }}>
            {PAY_STATUS_LABEL[s]}
          </Chip>
        ))}
      </div>

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
        <EmptyState title="Платежей пока нет" description="Здесь появятся все платежи платформы." mood="idle" />
      ) : (
        <Card className="p-0">
          <ul className="divide-y divide-line">
            {data.items.map((p) => (
              <li key={p.id} className="flex flex-wrap items-center gap-3 px-4 py-3">
                <div className="flex-1">
                  <div className="font-bold text-ink">{p.payer_email ?? '—'}</div>
                  <div className="text-xs text-hint">
                    {PLAN_LABEL[p.plan] ?? p.plan}
                    {p.receipt_no && ` · ${p.receipt_no}`}
                    {p.paid_at && ` · ${formatDate(p.paid_at)}`}
                  </div>
                </div>
                <span className="font-extrabold text-ink">{formatMoney(p.amount)}</span>
                <Badge tone={PAY_TONE[p.status] ?? 'muted'}>{PAY_STATUS_LABEL[p.status] ?? p.status}</Badge>
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

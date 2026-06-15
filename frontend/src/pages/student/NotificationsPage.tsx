import { Award, Bell, Calendar, CheckCheck, CreditCard, FileCheck, type LucideIcon } from 'lucide-react'

import { Button, Card, EmptyState, Skeleton } from '../../components/ui'
import {
  useMarkAllReadMutation,
  useMarkReadMutation,
  useNotificationsQuery,
} from '../../features/notifications/api'
import { cn } from '../../lib/cn'
import { formatDateTime } from '../../lib/format'

const META: Record<string, { icon: LucideIcon; text: string }> = {
  work_checked: { icon: FileCheck, text: 'Работа проверена' },
  new_session: { icon: Calendar, text: 'Новое занятие' },
  deadline: { icon: Bell, text: 'Напоминание о дедлайне' },
  achievement: { icon: Award, text: 'Новое достижение!' },
  payment_status: { icon: CreditCard, text: 'Статус оплаты' },
}

export function NotificationsPage() {
  const { data, isLoading } = useNotificationsQuery()
  const [markRead] = useMarkReadMutation()
  const [markAll] = useMarkAllReadMutation()

  if (isLoading) return <Skeleton className="h-60 w-full rounded-xl" />
  if (!data || data.length === 0) {
    return <EmptyState title="Нет уведомлений" description="Здесь появятся новости об учёбе и наградах." mood="idle" />
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-extrabold text-ink">Уведомления</h1>
        <Button variant="ghost" onClick={() => markAll()}>
          <CheckCheck className="h-4 w-4" aria-hidden /> Прочитать всё
        </Button>
      </div>
      <div className="space-y-2">
        {data.map((n) => {
          const meta = META[n.type] ?? META.work_checked
          const Icon = meta.icon
          return (
            <Card
              key={n.id}
              className={cn('flex cursor-pointer items-start gap-3', !n.is_read && 'border-brand-200 bg-brand-50')}
              onClick={() => !n.is_read && markRead(n.id)}
            >
              <span className="flex h-9 w-9 items-center justify-center rounded-md bg-surface text-brand">
                <Icon className="h-5 w-5" aria-hidden />
              </span>
              <div className="flex-1">
                <div className="font-bold text-ink">{meta.text}</div>
                <div className="text-xs text-hint">{formatDateTime(n.created_at)}</div>
              </div>
              {!n.is_read && <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-coral" />}
            </Card>
          )
        })}
      </div>
    </div>
  )
}

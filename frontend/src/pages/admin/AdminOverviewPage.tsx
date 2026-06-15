import { Card, Skeleton } from '../../components/ui'
import { useAdminOverviewQuery } from '../../features/admin/api'
import { formatMoney } from '../../lib/format'
import { ROLE_LABEL } from '../../lib/roles'

function Tile({ label, value }: { label: string; value: string }) {
  return (
    <Card className="text-center">
      <div className="text-2xl font-extrabold text-ink">{value}</div>
      <div className="text-xs text-muted">{label}</div>
    </Card>
  )
}

export function AdminOverviewPage() {
  const { data, isLoading } = useAdminOverviewQuery()
  if (isLoading || !data) return <Skeleton className="h-60 w-full rounded-xl" />

  const roleRows = Object.entries(data.users).filter(([k]) => k !== 'total')

  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-extrabold text-ink">Сводка платформы</h1>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-3 lg:grid-cols-6">
        <Tile label="Пользователей" value={String(data.users.total ?? 0)} />
        <Tile label="Записей" value={String(data.enrollments)} />
        <Tile label="Отправок" value={String(data.submissions)} />
        <Tile label="Активных 7д" value={String(data.active_students_7d)} />
        <Tile label="Выручка" value={formatMoney(data.revenue_total)} />
        <Tile label="Платежей" value={String(data.payments_count)} />
      </div>

      <div className="grid gap-4 sm:grid-cols-2">
        <Card>
          <h2 className="mb-3 text-lg font-extrabold text-ink">Пользователи по ролям</h2>
          <div className="space-y-2">
            {roleRows.map(([role, count]) => (
              <div key={role} className="flex items-center justify-between">
                <span className="text-muted">{ROLE_LABEL[role as keyof typeof ROLE_LABEL] ?? role}</span>
                <span className="font-extrabold text-ink">{count}</span>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <h2 className="mb-3 text-lg font-extrabold text-ink">Популярные курсы</h2>
          {data.popular_courses.length === 0 ? (
            <p className="text-muted">Нет данных.</p>
          ) : (
            <ol className="space-y-2">
              {data.popular_courses.map((c, i) => (
                <li key={c.course_id} className="flex items-center gap-3">
                  <span className="w-5 font-extrabold text-hint">{i + 1}</span>
                  <span className="flex-1 text-ink">{c.title}</span>
                  <span className="text-sm font-bold text-brand">{c.enrollments} зап.</span>
                </li>
              ))}
            </ol>
          )}
        </Card>
      </div>
    </div>
  )
}

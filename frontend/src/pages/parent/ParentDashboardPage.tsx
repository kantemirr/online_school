import { CreditCard, Users, Wallet, type LucideIcon } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Kodik } from '../../components/mascot/Kodik'
import { Avatar, Button, Card, EmptyState, ProgressBar, Skeleton } from '../../components/ui'
import { useParentOverviewQuery } from '../../features/analytics/api'
import { formatMoney } from '../../lib/format'
import { useAppSelector } from '../../store/hooks'

function Tile({ icon: Icon, tone, label, value }: { icon: LucideIcon; tone: string; label: string; value: string }) {
  return (
    <Card className="flex items-center gap-3">
      <span className={`flex h-11 w-11 items-center justify-center rounded-md ${tone}`}>
        <Icon className="h-6 w-6" aria-hidden />
      </span>
      <div>
        <div className="text-sm text-muted">{label}</div>
        <div className="text-xl font-extrabold text-ink">{value}</div>
      </div>
    </Card>
  )
}

export function ParentDashboardPage() {
  const { data, isLoading } = useParentOverviewQuery()
  const name = useAppSelector((s) => s.auth.user?.display_name) ?? 'родитель'

  if (isLoading || !data) return <Skeleton className="h-60 w-full rounded-xl" />

  return (
    <div className="space-y-6">
      <Card className="flex flex-col items-center gap-5 border-0 bg-brand text-white sm:flex-row">
        <Kodik mood="wave" size={88} aria-hidden />
        <div className="text-center sm:text-left">
          <h1 className="text-2xl font-extrabold">Здравствуйте, {name}!</h1>
          <p className="mt-1 text-white/85">Следите за успехами детей и управляйте абонементами.</p>
          <Link to="/parent/payments" className="mt-4 inline-block">
            <Button variant="reward">Оформить абонемент</Button>
          </Link>
        </div>
      </Card>

      <div className="grid grid-cols-1 gap-3 sm:grid-cols-3">
        <Tile icon={Wallet} tone="bg-teal-50 text-teal-700" label="Потрачено" value={formatMoney(data.expenses.total_spent)} />
        <Tile icon={CreditCard} tone="bg-brand-50 text-brand-700" label="Платежей" value={String(data.expenses.payments_count)} />
        <Tile icon={Users} tone="bg-sun-50 text-sun-700" label="Активных абонементов" value={String(data.expenses.active_subscriptions)} />
      </div>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-extrabold text-ink">Мои дети</h2>
          <Link to="/parent/children" className="text-sm font-bold text-brand">
            Управление
          </Link>
        </div>
        {data.children.length === 0 ? (
          <EmptyState
            title="Пока нет профилей детей"
            description="Добавьте профиль ребёнка — он сможет входить по логину и PIN."
            mood="happy"
            action={
              <Link to="/parent/children">
                <Button>Добавить ребёнка</Button>
              </Link>
            }
          />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2">
            {data.children.map((c) => (
              <Card key={c.child_id}>
                <div className="flex items-center gap-3">
                  <Avatar name={c.nickname} />
                  <div className="flex-1">
                    <div className="font-extrabold text-ink">{c.nickname}</div>
                    <div className="text-xs text-hint">
                      {c.xp.toLocaleString('ru-RU')} XP · серия {c.streak}
                    </div>
                  </div>
                </div>
                <div className="mt-3">
                  <ProgressBar value={c.avg_progress} />
                  <p className="mt-1 text-xs text-hint">
                    Средний прогресс {Math.round(c.avg_progress)}% · курсов {c.courses_enrolled}, пройдено {c.courses_completed}
                  </p>
                </div>
                <Link to={`/parent/children/${c.child_id}`}>
                  <Button variant="secondary" className="mt-3 w-full">
                    Отчёт об успеваемости
                  </Button>
                </Link>
              </Card>
            ))}
          </div>
        )}
      </section>
    </div>
  )
}

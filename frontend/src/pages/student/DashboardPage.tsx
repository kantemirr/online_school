import { Crown, Flame, Star, Trophy, type LucideIcon } from 'lucide-react'
import { Link } from 'react-router-dom'

import { Kodik } from '../../components/mascot/Kodik'
import { Badge, Button, Card, EmptyState, ProgressBar, Skeleton } from '../../components/ui'
import { useStudentDashboardQuery } from '../../features/analytics/api'
import { useAppSelector } from '../../store/hooks'

function StatTile({ icon: Icon, tone, label, value }: { icon: LucideIcon; tone: string; label: string; value: string }) {
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

export function DashboardPage() {
  const { data, isLoading } = useStudentDashboardQuery()
  const name = useAppSelector((s) => s.auth.user?.display_name) ?? 'друг'

  if (isLoading || !data) {
    return (
      <div className="space-y-6">
        <Skeleton className="h-40 w-full rounded-xl" />
        <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
          {Array.from({ length: 4 }).map((_, i) => (
            <Skeleton key={i} className="h-20 rounded-xl" />
          ))}
        </div>
      </div>
    )
  }

  const resume = data.courses.find((c) => c.status === 'active')

  return (
    <div className="space-y-6">
      <Card className="flex flex-col items-center gap-5 border-0 bg-brand text-white sm:flex-row">
        <Kodik mood="wave" size={96} aria-hidden />
        <div className="text-center sm:text-left">
          <h1 className="text-2xl font-extrabold">Привет, {name}!</h1>
          <p className="mt-1 text-white/85">
            {data.streak > 0 ? `Ты на ${data.streak}-дневной серии — так держать!` : 'Готов учиться сегодня?'}
          </p>
          <div className="mt-4 flex flex-wrap justify-center gap-3 sm:justify-start">
            {resume ? (
              <Link to={`/learn/${resume.course_id}`}>
                <Button variant="reward">Продолжить обучение</Button>
              </Link>
            ) : (
              <Link to="/catalog">
                <Button variant="reward">Выбрать курс</Button>
              </Link>
            )}
            <Link to="/leaderboard">
              <Button variant="secondary" className="border-white/30 bg-white/15 text-white">
                Рейтинг
              </Button>
            </Link>
          </div>
        </div>
      </Card>

      <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
        <StatTile icon={Star} tone="bg-sun-50 text-sun-700" label="Очки опыта" value={data.xp.toLocaleString('ru-RU')} />
        <StatTile icon={Flame} tone="bg-coral-50 text-coral-700" label="Серия дней" value={String(data.streak)} />
        <StatTile icon={Crown} tone="bg-brand-50 text-brand-700" label="Ранг" value={data.rank_global ? `#${data.rank_global}` : '—'} />
        <StatTile icon={Trophy} tone="bg-teal-50 text-teal-700" label="Награды" value={`${data.achievements_earned}/${data.achievements_total}`} />
      </div>

      <section>
        <div className="mb-3 flex items-center justify-between">
          <h2 className="text-lg font-extrabold text-ink">Мои курсы</h2>
          <Link to="/catalog" className="text-sm font-bold text-brand">
            Все курсы
          </Link>
        </div>
        {data.courses.length === 0 ? (
          <EmptyState
            title="Пока нет курсов"
            description="Запишись на первый курс и начни приключение в программировании!"
            mood="happy"
            action={
              <Link to="/catalog">
                <Button>Выбрать курс</Button>
              </Link>
            }
          />
        ) : (
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.courses.map((c) => (
              <Card key={c.course_id}>
                <div className="mb-2 flex items-center justify-between">
                  <h3 className="text-lg font-extrabold text-ink">{c.title}</h3>
                  {c.status === 'completed' && <Badge tone="success">Пройден</Badge>}
                </div>
                <p className="mb-3 text-sm text-muted">Завершено уроков: {c.completed_lessons}</p>
                <ProgressBar value={c.progress_pct} />
                <p className="mt-2 text-xs text-hint">Прогресс {Math.round(c.progress_pct)}%</p>
                <Link to={`/learn/${c.course_id}`}>
                  <Button className="mt-4 w-full" variant={c.progress_pct > 0 ? 'primary' : 'secondary'}>
                    {c.status === 'completed' ? 'Повторить' : 'Продолжить'}
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

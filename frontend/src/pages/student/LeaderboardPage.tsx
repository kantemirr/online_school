import { Card, EmptyState, Skeleton } from '../../components/ui'
import { useLeaderboardQuery } from '../../features/gamification/api'
import { cn } from '../../lib/cn'
import { useAppSelector } from '../../store/hooks'

export function LeaderboardPage() {
  const { data, isLoading } = useLeaderboardQuery(20)
  const myId = useAppSelector((s) => s.auth.user?.id)

  if (isLoading || !data) return <Skeleton className="h-72 w-full rounded-xl" />
  if (data.entries.length === 0) {
    return <EmptyState title="Рейтинг пока пуст" description="Проходи уроки и зарабатывай XP, чтобы попасть в топ!" mood="idle" />
  }

  const meInList = data.entries.some((e) => e.student_id === myId)

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-extrabold text-ink">Рейтинг</h1>
      <Card className="overflow-hidden p-0">
        <ul className="divide-y divide-line">
          {data.entries.map((e) => {
            const me = e.student_id === myId
            return (
              <li key={e.student_id} className={cn('flex items-center gap-3 px-4 py-3', me && 'bg-brand-50')}>
                <span className={cn('w-8 text-center font-extrabold', e.rank <= 3 ? 'text-sun-700' : 'text-hint')}>
                  #{e.rank}
                </span>
                <span className="flex-1 font-bold text-ink">
                  {e.nickname ?? 'Аноним'}
                  {me && ' (ты)'}
                </span>
                <span className="font-extrabold text-brand">{Math.round(e.score)}</span>
              </li>
            )
          })}
        </ul>
      </Card>
      {data.my_rank && !meInList && (
        <Card className="flex items-center gap-3">
          <span className="font-bold text-ink">Твоё место: #{data.my_rank}</span>
          <span className="ml-auto font-extrabold text-brand">{Math.round(data.my_score ?? 0)}</span>
        </Card>
      )}
    </div>
  )
}

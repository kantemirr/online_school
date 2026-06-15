import { Lock, Trophy } from 'lucide-react'

import { Card, Skeleton } from '../../components/ui'
import { useAchievementsQuery, useGamiMeQuery } from '../../features/gamification/api'
import { cn } from '../../lib/cn'
import { formatDate } from '../../lib/format'

export function AchievementsPage() {
  const { data, isLoading } = useAchievementsQuery()
  const { data: me } = useGamiMeQuery()

  if (isLoading || !data) {
    return (
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {Array.from({ length: 6 }).map((_, i) => (
          <Skeleton key={i} className="h-36 rounded-xl" />
        ))}
      </div>
    )
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-extrabold text-ink">Награды</h1>
        {me && (
          <span className="font-bold text-muted">
            {me.achievements_earned} из {me.achievements_total}
          </span>
        )}
      </div>
      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4">
        {data.map((a) => (
          <Card key={a.code} className={cn('flex flex-col items-center gap-2 text-center', !a.earned && 'opacity-60')}>
            <span
              className={cn(
                'flex h-14 w-14 items-center justify-center rounded-full',
                a.earned ? 'bg-sun-50 text-sun-700' : 'bg-line text-hint',
              )}
            >
              {a.earned ? <Trophy className="h-7 w-7" aria-hidden /> : <Lock className="h-6 w-6" aria-hidden />}
            </span>
            <div className="font-bold text-ink">{a.title}</div>
            {a.description && <div className="text-xs text-muted">{a.description}</div>}
            {a.earned && a.earned_at && <div className="text-xs text-hint">{formatDate(a.earned_at)}</div>}
          </Card>
        ))}
      </div>
    </div>
  )
}

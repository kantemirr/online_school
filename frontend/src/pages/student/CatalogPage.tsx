import { useState } from 'react'

import { Search } from 'lucide-react'

import { Button, EmptyState, Input, Skeleton } from '../../components/ui'
import { useCoursesQuery, useTracksQuery } from '../../features/catalog/api'
import { CourseCard } from '../../features/catalog/CourseCard'
import { cn } from '../../lib/cn'
import { LEVEL_LABEL } from '../../lib/labels'
import { useDebounced } from '../../lib/useDebounced'

const LEVELS = ['beginner', 'intermediate', 'advanced']
const PAGE_SIZE = 9

export function CatalogPage() {
  const [track, setTrack] = useState<string | undefined>()
  const [level, setLevel] = useState<string | undefined>()
  const [rawQ, setRawQ] = useState('')
  const [page, setPage] = useState(1)
  const q = useDebounced(rawQ)

  const { data: tracks } = useTracksQuery()
  const { data, isFetching } = useCoursesQuery({
    track,
    level,
    q: q || undefined,
    page,
    size: PAGE_SIZE,
  })

  const reset = (fn: () => void) => {
    fn()
    setPage(1)
  }
  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1

  return (
    <div className="space-y-5">
      <h1 className="text-2xl font-extrabold text-ink">Каталог курсов</h1>

      <div className="relative">
        <Search className="pointer-events-none absolute left-3 top-1/2 h-5 w-5 -translate-y-1/2 text-hint" aria-hidden />
        <Input
          className="pl-10"
          placeholder="Поиск курса…"
          value={rawQ}
          onChange={(e) => reset(() => setRawQ(e.target.value))}
        />
      </div>

      <div className="flex flex-wrap gap-2">
        <Chip active={!track} onClick={() => reset(() => setTrack(undefined))}>
          Все направления
        </Chip>
        {tracks?.map((t) => (
          <Chip key={t.code} active={track === t.code} onClick={() => reset(() => setTrack(t.code))}>
            {t.label} · {t.course_count}
          </Chip>
        ))}
      </div>

      <div className="flex flex-wrap gap-2">
        <Chip active={!level} onClick={() => reset(() => setLevel(undefined))}>
          Любой уровень
        </Chip>
        {LEVELS.map((l) => (
          <Chip key={l} active={level === l} onClick={() => reset(() => setLevel(l))}>
            {LEVEL_LABEL[l]}
          </Chip>
        ))}
      </div>

      {isFetching && !data ? (
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {Array.from({ length: 6 }).map((_, i) => (
            <Skeleton key={i} className="h-44 rounded-xl" />
          ))}
        </div>
      ) : data && data.items.length > 0 ? (
        <>
          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {data.items.map((c) => (
              <CourseCard key={c.id} course={c} />
            ))}
          </div>
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-3">
              <Button variant="ghost" disabled={page <= 1} onClick={() => setPage((p) => p - 1)}>
                Назад
              </Button>
              <span className="text-sm font-bold text-muted">
                {page} / {totalPages}
              </span>
              <Button variant="ghost" disabled={page >= totalPages} onClick={() => setPage((p) => p + 1)}>
                Вперёд
              </Button>
            </div>
          )}
        </>
      ) : (
        <EmptyState
          title="Ничего не найдено"
          description="Попробуй изменить фильтры или поиск."
          mood="thinking"
          action={
            <Button
              variant="secondary"
              onClick={() => {
                setTrack(undefined)
                setLevel(undefined)
                setRawQ('')
                setPage(1)
              }}
            >
              Сбросить фильтры
            </Button>
          }
        />
      )}
    </div>
  )
}

function Chip({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={cn(
        'rounded-full px-4 py-1.5 text-sm font-bold transition',
        active ? 'bg-brand text-white' : 'bg-surface text-muted border border-line hover:border-brand-200',
      )}
    >
      {children}
    </button>
  )
}

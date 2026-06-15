import { type ReactNode } from 'react'

import { Kodik, type KodikMood } from '../mascot/Kodik'

interface EmptyStateProps {
  title: string
  description?: string
  mood?: KodikMood
  action?: ReactNode
}

export function EmptyState({ title, description, mood = 'idle', action }: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center gap-3 rounded-xl border border-line bg-surface p-8 text-center">
      <Kodik mood={mood} size={104} aria-hidden />
      <h3 className="text-xl font-extrabold text-ink">{title}</h3>
      {description && <p className="max-w-sm text-muted">{description}</p>}
      {action}
    </div>
  )
}

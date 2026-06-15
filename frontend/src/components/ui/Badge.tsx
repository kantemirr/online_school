import { type HTMLAttributes } from 'react'

import { cn } from '../../lib/cn'

type Tone = 'brand' | 'teal' | 'sun' | 'coral' | 'success' | 'danger' | 'muted'

const TONES: Record<Tone, string> = {
  brand: 'bg-brand-50 text-brand-700',
  teal: 'bg-teal-50 text-teal-700',
  sun: 'bg-sun-50 text-sun-ink',
  coral: 'bg-coral-50 text-coral-700',
  success: 'bg-success-50 text-success-700',
  danger: 'bg-danger-50 text-danger-700',
  muted: 'bg-line text-muted',
}

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: Tone
}

export function Badge({ tone = 'brand', className, ...rest }: BadgeProps) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full px-3 py-1 text-xs font-extrabold',
        TONES[tone],
        className,
      )}
      {...rest}
    />
  )
}

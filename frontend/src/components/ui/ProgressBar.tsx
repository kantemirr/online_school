import { motion } from 'framer-motion'

import { cn } from '../../lib/cn'

interface ProgressBarProps {
  value: number
  className?: string
}

/** Анимированный прогресс-бар (плавно «дотекает» до значения). */
export function ProgressBar({ value, className }: ProgressBarProps) {
  const pct = Math.max(0, Math.min(100, Math.round(value)))
  return (
    <div
      className={cn('h-2.5 w-full overflow-hidden rounded-full bg-brand-50', className)}
      role="progressbar"
      aria-valuenow={pct}
      aria-valuemin={0}
      aria-valuemax={100}
    >
      <motion.div
        className="h-full rounded-full bg-brand"
        initial={{ width: 0 }}
        animate={{ width: `${pct}%` }}
        transition={{ type: 'spring', stiffness: 120, damping: 20 }}
      />
    </div>
  )
}

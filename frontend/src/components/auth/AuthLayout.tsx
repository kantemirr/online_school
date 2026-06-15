import { type ReactNode } from 'react'

import { Kodik, type KodikMood } from '../mascot/Kodik'

interface AuthLayoutProps {
  title: string
  subtitle?: string
  mood?: KodikMood
  children: ReactNode
  footer?: ReactNode
}

export function AuthLayout({ title, subtitle, mood = 'wave', children, footer }: AuthLayoutProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-cloud p-4">
      <div className="w-full max-w-md">
        <div className="mb-4 flex flex-col items-center text-center">
          <Kodik mood={mood} size={88} aria-hidden />
          <h1 className="mt-2 text-2xl font-extrabold text-ink">{title}</h1>
          {subtitle && <p className="text-muted">{subtitle}</p>}
        </div>
        <div className="rounded-2xl border border-line bg-surface p-6 shadow-card">{children}</div>
        {footer && <div className="mt-4 text-center text-sm text-muted">{footer}</div>}
      </div>
    </div>
  )
}

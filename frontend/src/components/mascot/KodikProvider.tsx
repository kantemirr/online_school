import { createContext, useCallback, useContext, useMemo, useRef, useState, type ReactNode } from 'react'

import { Kodik, type KodikMood } from './Kodik'

interface KodikContextValue {
  mood: KodikMood
  /** Временно показать настроение маскота (по умолчанию 2.2с), затем вернуть idle. */
  react: (mood: KodikMood, ms?: number) => void
}

const KodikContext = createContext<KodikContextValue | null>(null)

export function KodikProvider({ children }: { children: ReactNode }) {
  const [mood, setMood] = useState<KodikMood>('idle')
  const timer = useRef<ReturnType<typeof setTimeout>>()

  const react = useCallback((next: KodikMood, ms = 2200) => {
    setMood(next)
    if (timer.current) clearTimeout(timer.current)
    timer.current = setTimeout(() => setMood('idle'), ms)
  }, [])

  const value = useMemo(() => ({ mood, react }), [mood, react])
  return <KodikContext.Provider value={value}>{children}</KodikContext.Provider>
}

export function useKodik(): KodikContextValue {
  const ctx = useContext(KodikContext)
  if (!ctx) throw new Error('useKodik должен использоваться внутри <KodikProvider>')
  return ctx
}

/** Маскот, отражающий текущее глобальное настроение из контекста. */
export function KodikReaction({ size = 96 }: { size?: number }) {
  const { mood } = useKodik()
  return <Kodik mood={mood} size={size} />
}

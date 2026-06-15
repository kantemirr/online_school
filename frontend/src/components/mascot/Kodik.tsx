import { motion, useReducedMotion } from 'framer-motion'

import { cn } from '../../lib/cn'

export type KodikMood = 'idle' | 'happy' | 'thinking' | 'celebrate' | 'sad' | 'wave'

interface KodikProps {
  mood?: KodikMood
  size?: number
  className?: string
  'aria-hidden'?: boolean
}

const MOUTHS: Record<KodikMood, string> = {
  idle: 'M48 58 Q60 64 72 58',
  happy: 'M46 56 Q60 70 74 56',
  celebrate: 'M46 56 Q60 72 74 56',
  thinking: 'M52 60 L70 60',
  sad: 'M48 64 Q60 54 72 64',
  wave: 'M48 57 Q60 66 72 57',
}

const CHEST: Record<KodikMood, string> = {
  idle: '#FF6B9D',
  wave: '#FF6B9D',
  happy: '#34C77B',
  celebrate: '#34C77B',
  thinking: '#FDB833',
  sad: '#F26D6D',
}

function Eyes({ mood }: { mood: KodikMood }) {
  const dark = '#082B3A'
  if (mood === 'happy' || mood === 'celebrate') {
    return (
      <g fill="none" stroke={dark} strokeWidth={3} strokeLinecap="round">
        <path d="M42 46 Q50 38 58 46" />
        <path d="M62 46 Q70 38 78 46" />
      </g>
    )
  }
  const cy = mood === 'sad' ? 48 : 46
  return (
    <g>
      <circle cx={50} cy={cy} r={4.5} fill={dark} />
      <circle cx={70} cy={cy} r={4.5} fill={dark} />
      <circle cx={51.6} cy={cy - 1.6} r={1.4} fill="#fff" />
      <circle cx={71.6} cy={cy - 1.6} r={1.4} fill="#fff" />
      {mood === 'sad' && (
        <g fill="none" stroke={dark} strokeWidth={2.4} strokeLinecap="round">
          <path d="M44 39 L56 42" />
          <path d="M76 39 L64 42" />
        </g>
      )}
      {mood === 'thinking' && (
        <path d="M44 39 Q50 36 56 39" fill="none" stroke={dark} strokeWidth={2.4} strokeLinecap="round" />
      )}
    </g>
  )
}

/** Маскот «Кодик» — дружелюбный робот, реагирующий настроением на события. */
export function Kodik({ mood = 'idle', size = 120, className, ...rest }: KodikProps) {
  // Уважаем prefers-reduced-motion: гасим декоративные JS-анимации Framer
  // (CSS-медиазапрос их не останавливает).
  const reduce = useReducedMotion()
  const bob = !reduce && (mood === 'idle' || mood === 'thinking')
  const wave = !reduce && (mood === 'wave' || mood === 'celebrate')
  const pulse = !reduce && mood === 'celebrate'

  return (
    <motion.svg
      width={size}
      height={size * 1.25}
      viewBox="0 0 120 150"
      className={cn('select-none', className)}
      role="img"
      aria-label="Маскот Кодик"
      animate={bob ? { y: [0, -6, 0] } : { y: 0 }}
      transition={bob ? { duration: 3, repeat: Infinity, ease: 'easeInOut' } : { duration: 0.2 }}
      {...rest}
    >
      <line x1="60" y1="8" x2="60" y2="22" stroke="#6C5CE7" strokeWidth="3" strokeLinecap="round" />
      <motion.circle
        cx="60"
        cy="8"
        r="6"
        fill="#FDB833"
        animate={pulse ? { scale: [1, 1.4, 1] } : { scale: 1 }}
        transition={pulse ? { duration: 0.6, repeat: Infinity } : { duration: 0.2 }}
        style={{ transformOrigin: '60px 8px' }}
      />

      {/* Светлый контур (stroke) делает силуэт читаемым даже на индиго-фоне (bg-brand). */}
      <rect x="12" y="88" width="13" height="28" rx="6.5" fill="#5544D6" stroke="#FFFFFF" strokeWidth="2" />
      <motion.rect
        x="95"
        y="84"
        width="13"
        height="28"
        rx="6.5"
        fill="#5544D6"
        stroke="#FFFFFF"
        strokeWidth="2"
        style={{ transformBox: 'fill-box', transformOrigin: 'top center' }}
        animate={wave ? { rotate: [0, -22, 6, -22, 0] } : { rotate: 12 }}
        transition={wave ? { duration: 1, repeat: Infinity, ease: 'easeInOut' } : { duration: 0.2 }}
      />

      <rect x="42" y="128" width="14" height="14" rx="6" fill="#5544D6" stroke="#FFFFFF" strokeWidth="2" />
      <rect x="64" y="128" width="14" height="14" rx="6" fill="#5544D6" stroke="#FFFFFF" strokeWidth="2" />

      <rect x="30" y="82" width="60" height="46" rx="16" fill="#6C5CE7" stroke="#FFFFFF" strokeWidth="2" />
      <circle cx="60" cy="104" r="7" fill={CHEST[mood]} />

      <rect x="20" y="22" width="80" height="58" rx="20" fill="#6C5CE7" stroke="#FFFFFF" strokeWidth="2" />
      <rect x="28" y="30" width="64" height="42" rx="13" fill="#0FA8A4" />
      <Eyes mood={mood} />
      <path d={MOUTHS[mood]} fill="none" stroke="#082B3A" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round" />
    </motion.svg>
  )
}

import { cn } from '../../lib/cn'

interface AvatarProps {
  name: string
  size?: number
  className?: string
}

export function Avatar({ name, size = 44, className }: AvatarProps) {
  const initials = name
    .trim()
    .split(/\s+/)
    .slice(0, 2)
    .map((w) => w[0]?.toUpperCase() ?? '')
    .join('')
  return (
    <div
      className={cn(
        'inline-flex items-center justify-center rounded-full bg-brand-50 font-extrabold text-brand-700',
        className,
      )}
      style={{ width: size, height: size, fontSize: Math.round(size * 0.4) }}
    >
      {initials || '?'}
    </div>
  )
}

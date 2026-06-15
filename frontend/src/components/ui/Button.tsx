import { forwardRef, type ButtonHTMLAttributes } from 'react'

import { Loader2 } from 'lucide-react'

import { cn } from '../../lib/cn'

type Variant = 'primary' | 'reward' | 'secondary' | 'ghost' | 'danger'
type Size = 'sm' | 'md' | 'lg'

const VARIANTS: Record<Variant, string> = {
  primary: 'bg-brand text-white hover:bg-brand-600 shadow-card',
  reward: 'bg-sun text-sun-ink hover:brightness-95 shadow-card',
  secondary: 'bg-white text-brand border-2 border-brand-200 hover:border-brand-400',
  ghost: 'text-brand hover:bg-brand-50',
  danger: 'bg-danger text-white hover:bg-danger-700 shadow-card',
}

const SIZES: Record<Size, string> = {
  sm: 'h-9 px-4 text-sm',
  md: 'h-11 px-5 text-base',
  lg: 'h-[52px] px-7 text-lg',
}

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  size?: Size
  loading?: boolean
  fullWidth?: boolean
}

export const Button = forwardRef<HTMLButtonElement, ButtonProps>(function Button(
  { variant = 'primary', size = 'md', loading = false, fullWidth, className, children, disabled, ...rest },
  ref,
) {
  return (
    <button
      ref={ref}
      disabled={disabled || loading}
      className={cn(
        'inline-flex items-center justify-center gap-2 rounded-md font-extrabold transition active:scale-[0.97] disabled:pointer-events-none disabled:opacity-60',
        VARIANTS[variant],
        SIZES[size],
        fullWidth && 'w-full',
        className,
      )}
      {...rest}
    >
      {loading && <Loader2 className="h-4 w-4 animate-spin" aria-hidden />}
      {children}
    </button>
  )
})

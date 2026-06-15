import { forwardRef, type InputHTMLAttributes, type ReactNode } from 'react'

import { cn } from '../../lib/cn'

export const Input = forwardRef<HTMLInputElement, InputHTMLAttributes<HTMLInputElement>>(
  function Input({ className, ...rest }, ref) {
    return (
      <input
        ref={ref}
        className={cn(
          'h-11 w-full rounded-md border-2 border-line bg-white px-4 text-base text-ink transition placeholder:text-hint focus:border-brand-400',
          className,
        )}
        {...rest}
      />
    )
  },
)

interface FieldProps {
  label: string
  hint?: string
  error?: string
  children: ReactNode
}

/** Обёртка поля формы: подпись + контрол + подсказка/ошибка. */
export function Field({ label, hint, error, children }: FieldProps) {
  return (
    <label className="block">
      <span className="mb-1.5 block text-sm font-bold text-muted">{label}</span>
      {children}
      {error ? (
        <span className="mt-1 block text-xs font-bold text-danger-700">{error}</span>
      ) : hint ? (
        <span className="mt-1 block text-xs text-hint">{hint}</span>
      ) : null}
    </label>
  )
}

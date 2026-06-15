import { describe, expect, it } from 'vitest'

import { cn } from '../cn'

describe('cn', () => {
  it('объединяет классы', () => {
    expect(cn('a', 'b')).toBe('a b')
  })

  it('разрешает конфликты Tailwind — побеждает последний', () => {
    expect(cn('p-2', 'p-4')).toBe('p-4')
    expect(cn('text-brand', 'text-white')).toBe('text-white')
  })

  it('игнорирует falsy-значения', () => {
    expect(cn('a', false && 'b', undefined, null, 'c')).toBe('a c')
  })
})

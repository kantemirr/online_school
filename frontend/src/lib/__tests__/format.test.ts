import { describe, expect, it } from 'vitest'

import { formatDate, formatMoney } from '../format'

describe('formatMoney', () => {
  it('форматирует число как рубли', () => {
    const s = formatMoney(990)
    expect(s).toContain('990')
    expect(s).toMatch(/₽|руб/i)
  })

  it('принимает строковую сумму', () => {
    expect(formatMoney('0')).toContain('0')
  })
})

describe('formatDate', () => {
  it('возвращает непустую дату для ISO-строки', () => {
    const s = formatDate('2026-06-15T10:00:00Z')
    expect(s).toBeTruthy()
    expect(s).toContain('2026')
  })
})

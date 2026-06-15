import { describe, expect, it } from 'vitest'

import { ROLE_HOME, ROLE_LABEL } from '../roles'
import type { UserRole } from '../types'

const ROLES: UserRole[] = ['student', 'parent', 'teacher', 'admin']

describe('roles', () => {
  it('у каждой роли есть домашний маршрут и подпись', () => {
    for (const r of ROLES) {
      expect(ROLE_HOME[r]).toMatch(/^\//)
      expect(ROLE_LABEL[r]).toBeTruthy()
    }
  })

  it('домашний маршрут ученика — /home', () => {
    expect(ROLE_HOME.student).toBe('/home')
  })

  it('маршруты ролей различны', () => {
    const homes = ROLES.map((r) => ROLE_HOME[r])
    expect(new Set(homes).size).toBe(ROLES.length)
  })
})

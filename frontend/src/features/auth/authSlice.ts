import { createSlice, type PayloadAction } from '@reduxjs/toolkit'

import type { UserRole } from '../../lib/types'

export interface AuthUser {
  id: number
  email: string | null
  role: UserRole
  display_name: string | null
}

interface AuthState {
  accessToken: string | null
  refreshToken: string | null
  user: AuthUser | null
}

const STORAGE_KEY = 'codekids_auth'

function load(): AuthState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw) as AuthState
  } catch {
    /* игнорируем повреждённое хранилище */
  }
  return { accessToken: null, refreshToken: null, user: null }
}

function persist(state: AuthState) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state))
}

const slice = createSlice({
  name: 'auth',
  initialState: load(),
  reducers: {
    setTokens(state, action: PayloadAction<{ accessToken: string; refreshToken: string }>) {
      state.accessToken = action.payload.accessToken
      state.refreshToken = action.payload.refreshToken
      persist(state)
    },
    setUser(state, action: PayloadAction<AuthUser | null>) {
      state.user = action.payload
      persist(state)
    },
    logout(state) {
      state.accessToken = null
      state.refreshToken = null
      state.user = null
      localStorage.removeItem(STORAGE_KEY)
    },
  },
})

export const { setTokens, setUser, logout } = slice.actions
export default slice.reducer

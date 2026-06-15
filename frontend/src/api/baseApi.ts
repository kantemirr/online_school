import {
  createApi,
  fetchBaseQuery,
  type BaseQueryFn,
  type FetchArgs,
  type FetchBaseQueryError,
} from '@reduxjs/toolkit/query/react'

import { logout, setTokens } from '../features/auth/authSlice'
import type { RootState } from '../store'

export interface Health {
  status: string
  db: boolean
  redis: boolean
}

const rawBaseQuery = fetchBaseQuery({
  baseUrl: '/api/v1',
  prepareHeaders: (headers, { getState }) => {
    const token = (getState() as RootState).auth.accessToken
    if (token) headers.set('Authorization', `Bearer ${token}`)
    return headers
  },
})

// На 401 пробуем обновить пару токенов через refresh и повторить запрос;
// при неудаче — разлогиниваем (RequireAuth уведёт на /login).
const baseQueryWithReauth: BaseQueryFn<string | FetchArgs, unknown, FetchBaseQueryError> = async (
  args,
  api,
  extraOptions,
) => {
  let result = await rawBaseQuery(args, api, extraOptions)
  if (result.error && result.error.status === 401) {
    const refreshToken = (api.getState() as RootState).auth.refreshToken
    if (refreshToken) {
      const refreshResult = await rawBaseQuery(
        { url: '/auth/refresh', method: 'POST', body: { refresh_token: refreshToken } },
        api,
        extraOptions,
      )
      if (refreshResult.data) {
        const data = refreshResult.data as { access_token: string; refresh_token: string }
        api.dispatch(setTokens({ accessToken: data.access_token, refreshToken: data.refresh_token }))
        result = await rawBaseQuery(args, api, extraOptions)
      } else {
        api.dispatch(logout())
      }
    } else {
      api.dispatch(logout())
    }
  }
  return result
}

export const baseApi = createApi({
  reducerPath: 'api',
  baseQuery: baseQueryWithReauth,
  tagTypes: [
    'Me',
    'Children',
    'Catalog',
    'Course',
    'Enrollment',
    'Lesson',
    'Submission',
    'GradingQueue',
    'Achievements',
    'Leaderboard',
    'Groups',
    'Schedule',
    'Notifications',
    'Payments',
    'Subscriptions',
    'AdminUsers',
    'AdminPayments',
    'AdminGroups',
    'AdminContent',
  ],
  endpoints: (builder) => ({
    health: builder.query<Health, void>({
      query: () => '/health',
    }),
  }),
})

export const { useHealthQuery } = baseApi

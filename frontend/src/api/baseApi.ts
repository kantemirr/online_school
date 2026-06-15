import { createApi, fetchBaseQuery } from '@reduxjs/toolkit/query/react'

export interface Health {
  status: string
  db: boolean
  redis: boolean
}

// Базовый клиент RTK Query: все запросы идут на /api/v1 (через nginx → FastAPI).
// Access-токен берётся из localStorage; полноценный refresh-перехват на 401 —
// под-этап аутентификации.
export const baseApi = createApi({
  reducerPath: 'api',
  baseQuery: fetchBaseQuery({
    baseUrl: '/api/v1',
    prepareHeaders: (headers) => {
      const token = localStorage.getItem('access_token')
      if (token) headers.set('Authorization', `Bearer ${token}`)
      return headers
    },
  }),
  tagTypes: ['Me', 'Catalog', 'Enrollment', 'Notifications'],
  endpoints: (builder) => ({
    health: builder.query<Health, void>({
      query: () => '/health',
    }),
  }),
})

export const { useHealthQuery } = baseApi

import { baseApi } from '../../api/baseApi'

export interface NotificationItem {
  id: number
  type: 'work_checked' | 'new_session' | 'deadline' | 'achievement' | 'payment_status'
  payload: Record<string, unknown>
  is_read: boolean
  created_at: string
}

export const notificationsApi = baseApi.injectEndpoints({
  endpoints: (b) => ({
    notifications: b.query<NotificationItem[], { unread_only?: boolean; limit?: number } | void>({
      query: (params) => ({ url: '/notifications', params: params ?? { limit: 50 } }),
      providesTags: ['Notifications'],
    }),
    unreadCount: b.query<{ count: number }, void>({
      query: () => '/notifications/unread-count',
      providesTags: ['Notifications'],
    }),
    markRead: b.mutation<void, number>({
      query: (id) => ({ url: `/notifications/${id}/read`, method: 'POST' }),
      invalidatesTags: ['Notifications'],
    }),
    markAllRead: b.mutation<void, void>({
      query: () => ({ url: '/notifications/read-all', method: 'POST' }),
      invalidatesTags: ['Notifications'],
    }),
  }),
})

export const {
  useNotificationsQuery,
  useUnreadCountQuery,
  useMarkReadMutation,
  useMarkAllReadMutation,
} = notificationsApi

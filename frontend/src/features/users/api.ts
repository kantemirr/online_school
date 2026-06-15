import { baseApi } from '../../api/baseApi'
import type { MeOut } from '../../lib/types'

export interface ChildOut {
  user_id: number
  nickname: string
  birth_date: string
  age_group: string
  login_username: string | null
  xp: number
  streak: number
}

export const usersApi = baseApi.injectEndpoints({
  endpoints: (b) => ({
    me: b.query<MeOut, void>({
      query: () => '/users/me',
      providesTags: ['Me'],
    }),
    children: b.query<ChildOut[], void>({
      query: () => '/children',
      providesTags: ['Children'],
    }),
    createChild: b.mutation<
      ChildOut,
      { nickname: string; birth_date: string; login_username: string; pin: string }
    >({
      query: (body) => ({ url: '/children', method: 'POST', body }),
      invalidatesTags: ['Children'],
    }),
    updateChild: b.mutation<ChildOut, { id: number; nickname?: string; pin?: string }>({
      query: ({ id, ...body }) => ({ url: `/children/${id}`, method: 'PATCH', body }),
      invalidatesTags: ['Children'],
    }),
    deleteChild: b.mutation<void, number>({
      query: (id) => ({ url: `/children/${id}`, method: 'DELETE' }),
      invalidatesTags: ['Children'],
    }),
  }),
})

export const {
  useMeQuery,
  useLazyMeQuery,
  useChildrenQuery,
  useCreateChildMutation,
  useUpdateChildMutation,
  useDeleteChildMutation,
} = usersApi

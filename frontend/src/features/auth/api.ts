import { baseApi } from '../../api/baseApi'
import type { MeOut, TokenPair } from '../../lib/types'

export const authApi = baseApi.injectEndpoints({
  endpoints: (b) => ({
    register: b.mutation<
      MeOut,
      { email: string; password: string; full_name: string; phone?: string; consent_pdn: boolean }
    >({
      query: (body) => ({ url: '/auth/register', method: 'POST', body }),
    }),
    verifyEmail: b.mutation<void, { token: string }>({
      query: (body) => ({ url: '/auth/verify-email', method: 'POST', body }),
    }),
    login: b.mutation<TokenPair, { email: string; password: string }>({
      query: (body) => ({ url: '/auth/login', method: 'POST', body }),
    }),
    childLogin: b.mutation<TokenPair, { login_username: string; pin: string }>({
      query: (body) => ({ url: '/auth/login/child', method: 'POST', body }),
    }),
    logout: b.mutation<void, { refresh_token: string }>({
      query: (body) => ({ url: '/auth/logout', method: 'POST', body }),
    }),
    resetRequest: b.mutation<{ status: string }, { email: string }>({
      query: (body) => ({ url: '/auth/password-reset/request', method: 'POST', body }),
    }),
    resetConfirm: b.mutation<void, { token: string; new_password: string }>({
      query: (body) => ({ url: '/auth/password-reset/confirm', method: 'POST', body }),
    }),
    changePassword: b.mutation<TokenPair, { old_password: string; new_password: string }>({
      query: (body) => ({ url: '/auth/change-password', method: 'POST', body }),
    }),
  }),
})

export const {
  useRegisterMutation,
  useVerifyEmailMutation,
  useLoginMutation,
  useChildLoginMutation,
  useLogoutMutation,
  useResetRequestMutation,
  useResetConfirmMutation,
  useChangePasswordMutation,
} = authApi

import { baseApi } from '../../api/baseApi'

export type PlanCode = 'course' | 'monthly' | 'annual'

export interface Subscription {
  id: number
  plan: PlanCode
  course_id: number | null
  period_start: string
  period_end: string
  status: 'pending' | 'active' | 'expired' | 'cancelled'
}

export interface Payment {
  id: number
  subscription_id: number
  amount: string | number
  status: 'pending' | 'paid' | 'failed' | 'refunded'
  paid_at: string | null
  receipt_no: string | null
}

export interface CheckoutOut {
  payment_id: number
  subscription_id: number
  amount: string | number
  status: string
  payment_url: string
}

export interface Receipt {
  receipt_no: string
  amount: string | number
  paid_at: string
  plan: PlanCode
  course_id: number | null
  period_start: string
  period_end: string
  payer: string | null
}

export const paymentsApi = baseApi.injectEndpoints({
  endpoints: (b) => ({
    subscriptions: b.query<Subscription[], void>({
      query: () => '/subscriptions',
      providesTags: ['Subscriptions'],
    }),
    payments: b.query<Payment[], void>({
      query: () => '/payments',
      providesTags: ['Payments'],
    }),
    receipt: b.query<Receipt, number>({
      query: (paymentId) => `/payments/${paymentId}/receipt`,
    }),
    checkout: b.mutation<CheckoutOut, { plan: PlanCode; course_id?: number }>({
      query: (body) => ({ url: '/payments/checkout', method: 'POST', body }),
    }),
    pay: b.mutation<Payment, { payment_id: number; outcome: 'paid' | 'failed' }>({
      query: ({ payment_id, outcome }) => ({
        url: `/payments/${payment_id}/pay`,
        method: 'POST',
        body: { outcome },
      }),
      invalidatesTags: ['Payments', 'Subscriptions'],
    }),
    cancelSubscription: b.mutation<Subscription, number>({
      query: (id) => ({ url: `/subscriptions/${id}/cancel`, method: 'POST' }),
      invalidatesTags: ['Payments', 'Subscriptions'],
    }),
  }),
})

export const {
  useSubscriptionsQuery,
  usePaymentsQuery,
  useLazyReceiptQuery,
  useCheckoutMutation,
  usePayMutation,
  useCancelSubscriptionMutation,
} = paymentsApi

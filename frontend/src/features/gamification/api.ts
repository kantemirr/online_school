import { baseApi } from '../../api/baseApi'

export interface GamiSummary {
  xp: number
  streak: number
  rank_global: number | null
  achievements_earned: number
  achievements_total: number
}

export interface Achievement {
  code: string
  title: string
  description: string | null
  icon: string | null
  earned: boolean
  earned_at: string | null
}

export interface LeaderEntry {
  rank: number
  student_id: number
  nickname: string | null
  score: number
}

export interface Leaderboard {
  entries: LeaderEntry[]
  my_rank: number | null
  my_score: number | null
}

export const gamificationApi = baseApi.injectEndpoints({
  endpoints: (b) => ({
    gamiMe: b.query<GamiSummary, void>({ query: () => '/gamification/me' }),
    achievements: b.query<Achievement[], void>({
      query: () => '/gamification/achievements',
      providesTags: ['Achievements'],
    }),
    leaderboard: b.query<Leaderboard, number | void>({
      query: (n) => `/gamification/leaderboard?n=${n ?? 20}`,
      providesTags: ['Leaderboard'],
    }),
  }),
})

export const { useGamiMeQuery, useAchievementsQuery, useLeaderboardQuery } = gamificationApi

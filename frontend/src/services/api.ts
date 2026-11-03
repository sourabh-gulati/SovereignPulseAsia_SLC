import axios from 'axios'

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api',
  timeout: 30000
})

export interface YieldPoint {
  tenor: string
  maturity_years: number
  yield_percent: number
}

export interface YieldCurve {
  source: string
  observation_date: string
  data_status: string
  yields: YieldPoint[]
}

export type SovereignTenor = '1Y' | '2Y' | '5Y' | '10Y'
export type IndiaGsecTenor = SovereignTenor
export interface IndiaGsecPoint { date: string; yield_percent: number }
export interface IndiaGsecHistory { source: string; tenor: SovereignTenor; data_status: string; points: IndiaGsecPoint[] }


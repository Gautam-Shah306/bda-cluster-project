export const API_BASE: string = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

export type UnauthorizedHandler = () => void;
let unauthorizedHandler: UnauthorizedHandler | null = null;
export const setUnauthorizedHandler = (fn: UnauthorizedHandler | null) => {
  unauthorizedHandler = fn;
};

interface ApiFetchOptions {
  method?: string;
  body?: unknown;
  auth?: boolean;
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { method = 'GET', body, auth = true } = options;
  const headers: Record<string, string> = {};
  
  const token = localStorage.getItem('token');
  const sentToken = auth && token !== null;
  
  if (sentToken) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(0, "", `Cannot reach the API at ${API_BASE}`);
  }

  if (!response.ok) {
    if (response.status === 401 && sentToken) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (unauthorizedHandler) {
        unauthorizedHandler();
      }
      throw new ApiError(401, "", "Unauthorized");
    }

    let detail = "";
    let message = `HTTP ${response.status}`;
    try {
      const errData = await response.json();
      if (errData && errData.detail) {
        if (typeof errData.detail === 'string') {
          detail = errData.detail;
          message = detail;
        } else if (Array.isArray(errData.detail) && errData.detail.length > 0 && errData.detail[0].msg) {
          detail = errData.detail[0].msg;
          message = detail;
        }
      }
    } catch {
      // ignore
    }
    
    throw new ApiError(response.status, detail, message);
  }

  return response.json();
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface SignupResponse {
  message: string;
}

export const loginApi = (credentials: Record<string, string>) => {
  return apiFetch<LoginResponse>('/auth/login', {
    method: 'POST',
    body: credentials,
    auth: false
  });
};

export const signupApi = (data: Record<string, string>) => {
  return apiFetch<SignupResponse>('/auth/signup', {
    method: 'POST',
    body: data,
    auth: false
  });
};


import {
  DashboardStats,
  HiringTrendPoint,
  SkillTrends,
  SkillGapRow,
  VulnerabilityResponse,
  LatestJob,
  CityDemand,
  RoleCount,
  NameValue
} from './dashboardTypes';

export const getDashboardStats = () => apiFetch<DashboardStats>('/dashboard/stats');
export const getHiringTrends = () => apiFetch<HiringTrendPoint[]>('/dashboard/hiring-trends');
export const getSkillTrends = (year?: number) => {
  const query = year !== undefined ? `?year=${year}` : '';
  return apiFetch<SkillTrends>(`/dashboard/skill-trends${query}`);
};
export const getSkillTrendYears = async (): Promise<number[]> => {
  const res = await apiFetch<{years: number[]}>('/dashboard/skill-trend-years');
  if (!res || !Array.isArray(res.years) || !res.years.every(y => typeof y === 'number')) {
    throw new ApiError(0, "", "Unexpected response from /dashboard/skill-trend-years");
  }
  return res.years;
};
export const getSkillGap = () => apiFetch<SkillGapRow[]>('/dashboard/skill-gap');
export const getVulnerability = () => apiFetch<VulnerabilityResponse>('/dashboard/vulnerability');
export const getLatestJobs = () => apiFetch<LatestJob[]>('/dashboard/latest-jobs');
export const getTopCities = () => apiFetch<CityDemand[]>('/dashboard/top-cities');
export const getTopRoles = () => apiFetch<RoleCount[]>('/dashboard/top-roles');
export const getRoleDistribution = (city: string) => apiFetch<NameValue[]>(`/dashboard/city-role-distribution?city=${encodeURIComponent(city)}`);
export const getCitySpread = (role: string) => apiFetch<NameValue[]>(`/dashboard/role-city-distribution?role=${encodeURIComponent(role)}`);

// ---- Worker, reskilling and chatbot (F3, D-033). Every response is normalized. ----
import {
  chatbotText,
  normalizeGeminiAnalysis,
  normalizeReskilling,
  normalizeWorkerProfile,
} from '../utils/workerData';
import type {
  GeminiAnalysis,
  ReskillingPlan,
  WorkerPayload,
  WorkerProfile,
} from './workerTypes';

/** GET /worker/profile, normalized. */
export const getWorkerProfile = async (): Promise<WorkerProfile> =>
  normalizeWorkerProfile(await apiFetch<unknown>('/worker/profile'));

/** POST /worker/profile; returns the normalized Gemini analysis. */
export const analyzeWorker = async (payload: WorkerPayload): Promise<GeminiAnalysis> => {
  const res = await apiFetch<unknown>('/worker/profile', { method: 'POST', body: payload });
  const analysis =
    typeof res === 'object' && res !== null ? (res as Record<string, unknown>).gemini_analysis : null;
  return normalizeGeminiAnalysis(analysis);
};

/** GET /worker/reskilling, normalized. */
export const getReskilling = async (): Promise<ReskillingPlan> =>
  normalizeReskilling(await apiFetch<unknown>('/worker/reskilling'));

/** POST /worker/reskilling (no body; can take up to two minutes), normalized. */
export const generateReskilling = async (): Promise<ReskillingPlan> =>
  normalizeReskilling(await apiFetch<unknown>('/worker/reskilling', { method: 'POST' }));

/** POST /chatbot/query. The profile is always {} (stateless, D-033). */
export const queryChatbot = async (question: string): Promise<string> =>
  chatbotText(
    await apiFetch<unknown>('/chatbot/query', {
      method: 'POST',
      body: { worker_profile: {}, question },
    }),
  );

// ----- Compatibility aliases for legacy imports (jobAnalytics) -----
export const getDashboardStatsApi = getDashboardStats;
export const getHiringTrendsApi = getHiringTrends;
export const getSkillTrendsApi = getSkillTrends;
export const getSkillTrendYearsApi = getSkillTrendYears;
export const getSkillGapApi = getSkillGap;
export const getVulnerabilityApi = getVulnerability;
export const getVulnerabilityRegionsApi = getVulnerability; // same endpoint
export const getLatestJobsApi = getLatestJobs;
export const getTopCitiesApi = getTopCities;
export const getIndustryDistributionApi = async () => [] as any[]; // placeholder until implemented
export const getTopRolesApi = getTopRoles;
export const getRoleDistributionApi = getRoleDistribution;
export const getCitySpreadApi = getCitySpread;
export const getScrapedJobsApi = async (_force?: boolean) => { /* no-op, placeholder */ return true; };

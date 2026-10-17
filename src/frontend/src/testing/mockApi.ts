import { vi } from 'vitest';

export interface MockConfig {
  body?: unknown;
  status?: number;
  delay?: number;
}

import {
  liveStats,
  liveHiringTrends,
  liveSkillTrends,
  liveSkillTrendYears,
  liveSkillGap,
  liveVulnerability,
  liveLatestJobs,
  liveTopCities,
  liveTopRoles,
  liveCityRoleDistribution,
  liveRoleCityDistribution,
  contractNewUserProfile,
  contractAnalyzeResponse,
  contractEmptyReskilling,
  contractReskillingPlan,
  contractChatbotCanned
} from './liveFixtures';

// Keys are "/path" (any method) or "METHOD /path" (that method only).
const defaultMocks: Record<string, unknown> = {
  '/dashboard/stats': liveStats,
  '/dashboard/hiring-trends': liveHiringTrends,
  '/dashboard/skill-trends': liveSkillTrends,
  '/dashboard/skill-trend-years': liveSkillTrendYears,
  '/dashboard/skill-gap': liveSkillGap,
  '/dashboard/vulnerability': liveVulnerability,
  '/dashboard/latest-jobs': liveLatestJobs,
  '/dashboard/top-cities': liveTopCities,
  '/dashboard/top-roles': liveTopRoles,
  '/dashboard/city-role-distribution': liveCityRoleDistribution,
  '/dashboard/role-city-distribution': liveRoleCityDistribution,
  'GET /worker/profile': contractNewUserProfile,
  'POST /worker/profile': contractAnalyzeResponse,
  'GET /worker/reskilling': contractEmptyReskilling,
  'POST /worker/reskilling': contractReskillingPlan,
  'POST /chatbot/query': contractChatbotCanned
};

export const recordedCalls: { method: string; url: string; body?: unknown }[] = [];
let overrides: Record<string, MockConfig> = {};

export function setupMockApi() {
  recordedCalls.length = 0;
  overrides = {};
  
  globalThis.fetch = vi.fn().mockImplementation(async (url: string | URL | Request, init?: RequestInit) => {
    const urlStr = url.toString();
    const method = init?.method || 'GET';
    let parsedBody: unknown = undefined;
    if (typeof init?.body === 'string') {
      try {
        parsedBody = JSON.parse(init.body);
      } catch {
        parsedBody = init.body;
      }
    }
    recordedCalls.push({ method, url: urlStr, body: parsedBody });
    
    const urlObj = new URL(urlStr);
    let path = urlObj.pathname;
    
    // Convert /api/v1/dashboard to /dashboard if API_BASE contains suffix
    if (path.startsWith('/api/v1')) {
      path = path.slice(7);
    } else if (path.startsWith('http://localhost:8000')) {
        path = path.slice(21);
    }
    
    // Overrides: "METHOD /path?query", "/path?query", "METHOD /path", "/path"
    const search = urlObj.search;
    const fullPath = path + search;
    const defaultBody = defaultMocks[`${method} ${path}`] !== undefined ? defaultMocks[`${method} ${path}`] : defaultMocks[path];
    
    const config =
      overrides[`${method} ${fullPath}`] ||
      overrides[fullPath] ||
      overrides[`${method} ${path}`] ||
      overrides[path] ||
      { status: 200, body: defaultBody };
    
    if (config.delay) {
      await new Promise(r => setTimeout(r, config.delay));
    }
    
    return {
      ok: config.status ? config.status < 400 : true,
      status: config.status || 200,
      json: async () => {
        if (config.body !== undefined) return config.body;
        if (defaultBody !== undefined) return defaultBody;
        return { detail: 'Not Found' };
      }
    };
  });
}

export function overrideMock(pathAndQuery: string, config: MockConfig) {
  overrides[pathAndQuery] = config;
}

export function restoreMockApi() {
  vi.restoreAllMocks();
}

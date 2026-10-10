export interface DashboardStats {
  total_jobs: number;
  top_city: string;
  most_in_demand_skill: string;
  most_common_role: string;
}

export interface HiringTrendPoint {
  month: string;
  job_count: number;
}

export interface RisingSkill {
  name: string;
  growth: string;
  color: string;
}

export interface DecliningSkill {
  name: string;
  decline: string;
}

export interface SkillTrends {
  rising_skills: RisingSkill[];
  declining_skills: DecliningSkill[];
}

export interface SkillGapRow {
  skill: string;
  market_demand: number;
  training_supply: number;
  gap: number;
}

export interface VulnerabilityRow {
  job_role: string;
  city: string;
  ai_risk_score: number;
}

export interface VulnerabilityResponse {
  table: VulnerabilityRow[];
  regions: Record<string, number>;
}

export interface LatestJob {
  jobtitle: string;
  company: string;
  location: string;
  skills: string;
  experience: string;
  postdate: string;
}

export interface CityDemand {
  name: string;
  demand: number;
}

export interface RoleCount {
  role: string;
  count: number;
}

export interface NameValue {
  name: string;
  value: number;
}



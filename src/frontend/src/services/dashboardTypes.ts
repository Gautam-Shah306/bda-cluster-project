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

export interface SkillItem {
  name: string;
  growth?: string;
  decline?: string;
  color?: string;
  type?: 'rising' | 'declining';
}

export interface SkillTrends {
  rising_skills: SkillItem[];
  declining_skills: SkillItem[];
}

export interface SkillGapRow {
  skill: string;
  market_demand: number;
  training_supply: number;
  gap: number;
}

export interface VulnerabilityTableRow {
  job_role: string;
  city: string;
  ai_risk_score: number;
  seq?: number;
}

export interface VulnerabilityResponse {
  table: VulnerabilityTableRow[];
  regions: Record<string, number>;
  role_risks?: Record<string, number>;
  region_risks?: Record<string, number>;
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

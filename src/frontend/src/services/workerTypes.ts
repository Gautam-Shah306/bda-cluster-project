/**
 * Types for the worker, reskilling and chatbot features.
 * These describe the NORMALIZED shapes the UI works with, not the raw API output,
 * because the API does not validate what Gemini returns (see utils/workerData.ts).
 */

export type RiskLevel = 'high' | 'moderate' | 'low' | 'unknown';

export interface GeminiAnalysis {
  riskScore: number | null;
  riskLevel: RiskLevel;
  pivotRoles: string[];
  newSkills: string[];
  explanation: string;
}

export interface WorkerProfile {
  jobRole: string;
  city: string;
  yearsOfExperience: number | null;
  roleDescription: string;
  skills: string[];
  analysis: GeminiAnalysis | null;
}

export interface WorkerPayload {
  job_role: string;
  city: string;
  years_of_experience: number;
  role_description: string;
  skills: string[];
}

export interface RecommendedSkill {
  skill: string;
  reason: string;
}

export interface RecommendedCourse {
  name: string;
  source: string;
  url: string;
  duration: string;
  matchedSkills: string[];
}

export interface RecommendedJob {
  title: string;
  company: string;
  location: string;
  requiredSkills: string[];
  matchReason: string;
}

export interface LearningStep {
  week: string;
  title: string;
  description: string;
}

export type RecommendationType = 'upskilling' | 'reskilling';

export interface ReskillingPlan {
  recommendationType: RecommendationType | null;
  summary: string;
  recommendedSkills: RecommendedSkill[];
  recommendedCourses: RecommendedCourse[];
  recommendedJobs: RecommendedJob[];
  learningPath: LearningStep[];
  error: string | null;
}

export type ScoreView =
  | { available: false }
  | { available: true; rounded: number; percent: number; label: string };

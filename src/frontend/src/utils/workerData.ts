/**
 * Pure normalizers and helpers for worker, reskilling and chatbot data.
 * Everything that comes from the API (and ultimately from an LLM) goes through
 * these functions, which accept `unknown` and never throw.
 */
import type {
  GeminiAnalysis,
  LearningStep,
  RecommendedCourse,
  RecommendedJob,
  RecommendedSkill,
  ReskillingPlan,
  RiskLevel,
  ScoreView,
  WorkerProfile,
} from '../services/workerTypes';

type Rec = Record<string, unknown>;

function isRecord(v: unknown): v is Rec {
  return typeof v === 'object' && v !== null && !Array.isArray(v);
}

function asString(v: unknown): string {
  return typeof v === 'string' ? v : '';
}

function asStringList(v: unknown): string[] {
  return Array.isArray(v) ? v.filter((x): x is string => typeof x === 'string') : [];
}

function asRecordList(v: unknown): Rec[] {
  return Array.isArray(v) ? v.filter(isRecord) : [];
}

/** Turns a number or numeric string into a finite number, else null. */
export function toScore(v: unknown): number | null {
  if (typeof v === 'number') return Number.isFinite(v) ? v : null;
  if (typeof v === 'string' && v.trim() !== '') {
    const n = Number(v);
    return Number.isFinite(n) ? n : null;
  }
  return null;
}

/** Normalizes a risk level; anything unexpected becomes "unknown". */
export function normalizeRiskLevel(v: unknown): RiskLevel {
  return v === 'high' || v === 'moderate' || v === 'low' ? v : 'unknown';
}

/** Normalizes the Gemini risk analysis. Always returns a complete object. */
export function normalizeGeminiAnalysis(raw: unknown): GeminiAnalysis {
  const r: Rec = isRecord(raw) ? raw : {};
  return {
    riskScore: toScore(r.risk_score),
    riskLevel: normalizeRiskLevel(r.risk_level),
    pivotRoles: asStringList(r.pivot_roles),
    newSkills: asStringList(r.new_skills),
    explanation: asString(r.explanation),
  };
}

/** Normalizes GET /worker/profile. A missing analysis stays null. */
export function normalizeWorkerProfile(raw: unknown): WorkerProfile {
  const r: Rec = isRecord(raw) ? raw : {};
  return {
    jobRole: asString(r.job_role),
    city: asString(r.city),
    yearsOfExperience: toScore(r.years_of_experience),
    roleDescription: asString(r.role_description),
    skills: asStringList(r.skills),
    analysis: isRecord(r.gemini_analysis) ? normalizeGeminiAnalysis(r.gemini_analysis) : null,
  };
}

/** Normalizes a reskilling plan (GET or POST /worker/reskilling). */
export function normalizeReskilling(raw: unknown): ReskillingPlan {
  const r: Rec = isRecord(raw) ? raw : {};
  const type =
    r.recommendation_type === 'upskilling' || r.recommendation_type === 'reskilling'
      ? r.recommendation_type
      : null;
  const skills: RecommendedSkill[] = asRecordList(r.recommended_skills).map((s) => ({
    skill: asString(s.skill),
    reason: asString(s.reason),
  }));
  const courses: RecommendedCourse[] = asRecordList(r.recommended_courses).map((c) => ({
    name: asString(c.name),
    source: asString(c.source),
    url: asString(c.url),
    duration: asString(c.duration),
    matchedSkills: asStringList(c.matched_skills),
  }));
  const jobs: RecommendedJob[] = asRecordList(r.recommended_jobs).map((j) => ({
    title: asString(j.title),
    company: asString(j.company),
    location: asString(j.location),
    requiredSkills: asStringList(j.required_skills),
    matchReason: asString(j.match_reason),
  }));
  const path: LearningStep[] = asRecordList(r.learning_path).map((s) => ({
    week: asString(s.week),
    title: asString(s.title),
    description: asString(s.description),
  }));
  const err = asString(r.error);
  return {
    recommendationType: type,
    summary: asString(r.summary),
    recommendedSkills: skills,
    recommendedCourses: courses,
    recommendedJobs: jobs,
    learningPath: path,
    error: err !== '' ? err : null,
  };
}

/** Returns the URL only when it is an absolute http(s) URL, else null. */
export function safeHttpUrl(v: unknown): string | null {
  if (typeof v !== 'string' || v.trim() === '') return null;
  try {
    const u = new URL(v.trim());
    return u.protocol === 'http:' || u.protocol === 'https:' ? u.toString() : null;
  } catch {
    return null;
  }
}

/** Describes how to show a risk score: rounded label, bar percent clamped to 0..100. */
export function scoreView(score: number | null): ScoreView {
  if (score === null || !Number.isFinite(score)) return { available: false };
  const rounded = Math.round(score);
  return {
    available: true,
    rounded,
    percent: Math.min(100, Math.max(0, rounded)),
    label: `${rounded}/100`,
  };
}

/** Splits a comma-separated skills field into trimmed, non-empty items. */
export function parseSkillsInput(s: string): string[] {
  return s
    .split(',')
    .map((x) => x.trim())
    .filter((x) => x.length > 0);
}

/** Extracts the chatbot text from a response body; falls back to "No response.". */
export function chatbotText(raw: unknown): string {
  if (isRecord(raw) && typeof raw.response === 'string' && raw.response !== '') {
    return raw.response;
  }
  return 'No response.';
}

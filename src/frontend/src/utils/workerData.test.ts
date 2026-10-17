import { describe, it, expect } from 'vitest';
import {
  chatbotText,
  normalizeGeminiAnalysis,
  normalizeReskilling,
  normalizeRiskLevel,
  normalizeWorkerProfile,
  parseSkillsInput,
  safeHttpUrl,
  scoreView,
  toScore,
} from './workerData';

const garbage: unknown[] = [null, undefined, 0, 42, 'text', '', [], [1, 2], { a: 1 }, NaN, true, () => 1];

describe('workerData normalizers never throw on garbage', () => {
  it.each(garbage.map((g, i) => [i, g]))('input #%i', (_i, g) => {
    expect(() => normalizeGeminiAnalysis(g)).not.toThrow();
    expect(() => normalizeWorkerProfile(g)).not.toThrow();
    expect(() => normalizeReskilling(g)).not.toThrow();
    expect(() => toScore(g)).not.toThrow();
    expect(() => safeHttpUrl(g)).not.toThrow();
    expect(() => chatbotText(g)).not.toThrow();
  });
  it('garbage becomes complete empty objects', () => {
    expect(normalizeGeminiAnalysis(null)).toEqual({ riskScore: null, riskLevel: 'unknown', pivotRoles: [], newSkills: [], explanation: '' });
    const plan = normalizeReskilling('x');
    expect(plan.recommendationType).toBeNull();
    expect(plan.learningPath).toEqual([]);
    expect(plan.error).toBeNull();
    expect(normalizeWorkerProfile(undefined).analysis).toBeNull();
  });
});

describe('score handling', () => {
  it('accepts numbers and numeric strings, rejects the rest', () => {
    expect(toScore(72)).toBe(72);
    expect(toScore('72')).toBe(72);
    expect(toScore(' 72.5 ')).toBe(72.5);
    expect(toScore('abc')).toBeNull();
    expect(toScore('')).toBeNull();
    expect(toScore(NaN)).toBeNull();
    expect(toScore(Infinity)).toBeNull();
    expect(toScore(null)).toBeNull();
  });
  it('scoreView rounds the label and clamps the bar', () => {
    expect(scoreView(null)).toEqual({ available: false });
    expect(scoreView(72.4)).toEqual({ available: true, rounded: 72, percent: 72, label: '72/100' });
    expect(scoreView(150)).toEqual({ available: true, rounded: 150, percent: 100, label: '150/100' });
    expect(scoreView(-5)).toEqual({ available: true, rounded: -5, percent: 0, label: '-5/100' });
  });
  it('risk level falls back to unknown', () => {
    expect(normalizeRiskLevel('high')).toBe('high');
    expect(normalizeRiskLevel('HIGH')).toBe('unknown');
    expect(normalizeRiskLevel(3)).toBe('unknown');
  });
});

describe('lists and items', () => {
  it('keeps only string items and drops non-lists', () => {
    const a = normalizeGeminiAnalysis({ pivot_roles: ['A', 1, null, 'B'], new_skills: 'oops', risk_score: '72', risk_level: 'low' });
    expect(a.pivotRoles).toEqual(['A', 'B']);
    expect(a.newSkills).toEqual([]);
    expect(a.riskScore).toBe(72);
    expect(a.riskLevel).toBe('low');
  });
  it('reskilling items missing fields get empty values', () => {
    const p = normalizeReskilling({
      recommendation_type: 'upskilling',
      recommended_skills: [{ skill: 'x' }, 5, null],
      recommended_courses: [{}, { name: 'C', matched_skills: [1, 'm'] }],
      recommended_jobs: 'nope',
      learning_path: null,
      error: '',
    });
    expect(p.recommendationType).toBe('upskilling');
    expect(p.recommendedSkills).toEqual([{ skill: 'x', reason: '' }]);
    expect(p.recommendedCourses).toHaveLength(2);
    expect(p.recommendedCourses[1].matchedSkills).toEqual(['m']);
    expect(p.recommendedJobs).toEqual([]);
    expect(p.error).toBeNull();
  });
  it('unknown recommendation types are dropped', () => {
    expect(normalizeReskilling({ recommendation_type: 'other' }).recommendationType).toBeNull();
  });
});

describe('safeHttpUrl', () => {
  it('allows only absolute http(s)', () => {
    expect(safeHttpUrl('https://a.example/x')).toBe('https://a.example/x');
    expect(safeHttpUrl('http://a.example/')).toBe('http://a.example/');
    expect(safeHttpUrl('javascript:alert(1)')).toBeNull();
    expect(safeHttpUrl('/relative')).toBeNull();
    expect(safeHttpUrl('')).toBeNull();
    expect(safeHttpUrl('data:text/html,hi')).toBeNull();
  });
});

describe('small helpers', () => {
  it('parseSkillsInput', () => {
    expect(parseSkillsInput(' a, b ,, ,c')).toEqual(['a', 'b', 'c']);
    expect(parseSkillsInput('')).toEqual([]);
  });
  it('chatbotText', () => {
    expect(chatbotText({ response: 'hi' })).toBe('hi');
    expect(chatbotText({ response: '' })).toBe('No response.');
    expect(chatbotText({})).toBe('No response.');
  });
});

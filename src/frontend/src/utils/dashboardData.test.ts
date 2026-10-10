import { describe, it, expect } from 'vitest';
import {
  formatName,
  formatCityName,
  truncateLabel,
  parseGrowth,
  topSkillsFromTrends,
  hiringSeries,
  gapSeries,
  regionSeries,
  riskLevel,
  formatDate,
  formatCount
} from './dashboardData';

describe('dashboardData', () => {
  it('formatName formats correctly', () => {
    expect(formatName('it software - application programming')).toBe('IT Software - Application Programming');
    expect(formatName('aws')).toBe('AWS');
    expect(formatName('react.js')).toBe('React.js');
    expect(formatName('customer service')).toBe('Customer Service');
    expect(formatName('')).toBe('');
  });

  it('formatCityName formats correctly', () => {
    expect(formatCityName('Bengaluru/Bangalore')).toBe('Bengaluru');
    expect(formatCityName('Mumbai')).toBe('Mumbai');
    expect(formatCityName('delhi ncr')).toBe('Delhi NCR');
    expect(formatCityName('Delhi/NCR(National Capital Region)')).toBe('Delhi');
    expect(formatCityName('Hyderabad / Secunderabad')).toBe('Hyderabad');
    expect(formatCityName('')).toBe('');
  });

  it('truncateLabel formats correctly', () => {
    expect(truncateLabel('123456789012345', 15)).toBe('123456789012345');
    expect(truncateLabel('1234567890123456', 15)).toBe('123456789012345...');
  });

  it('parseGrowth formats correctly', () => {
    expect(parseGrowth('+608')).toBe(608);
    expect(parseGrowth('abc')).toBe(0);
    expect(parseGrowth('123')).toBe(123);
  });

  it('topSkillsFromTrends works', () => {
    const trends = {
      rising_skills: [
        { name: 'it', growth: '+10', color: 'green' }
      ],
      declining_skills: []
    };
    expect(topSkillsFromTrends(trends)).toEqual([{ name: 'IT', growth: 10 }]);
  });

  it('hiringSeries works', () => {
    const pts = [{ month: '2026-01', job_count: 100 }];
    expect(hiringSeries(pts)).toEqual([{ name: '2026-01', jobs: 100, active: 80 }]);
  });

  it('gapSeries drops training_supply 0, sorts by market_demand, limits to 10', () => {
    const rows = [
      { skill: 'drop me', market_demand: 100, training_supply: 0, gap: 100 },
      { skill: 'first', market_demand: 200, training_supply: 2, gap: 198 },
      { skill: 'second', market_demand: 150, training_supply: 3, gap: 147 },
      ...Array.from({length: 10}).map((_, i) => ({ skill: `skill ${i}`, market_demand: 10, training_supply: 1, gap: 9 }))
    ];
    
    const res = gapSeries(rows);
    expect(res).toHaveLength(10);
    expect(res[0].name).toBe('First');
    expect(res[1].name).toBe('Second');
    // Ensure 'drop me' is omitted
    expect(res.map(r => r.name)).not.toContain('Drop Me');
  });

  it('regionSeries handles limits and breaks ties by name', () => {
    const regions = {
      'B': 50,
      'A': 50,
      'C': 30,
      ...Object.fromEntries(Array.from({length: 10}).map((_, i) => [`City${i}`, 10]))
    };
    
    const res = regionSeries(regions);
    expect(res).toHaveLength(8);
    expect(res[0]).toEqual({ name: 'A', risk: 50 });
    expect(res[1]).toEqual({ name: 'B', risk: 50 });
    expect(res[2]).toEqual({ name: 'C', risk: 30 });
  });

  it('riskLevel categorizes properly', () => {
    expect(riskLevel(60)).toBe('high');
    expect(riskLevel(59)).toBe('medium');
    expect(riskLevel(30)).toBe('medium');
    expect(riskLevel(29)).toBe('low');
  });

  it('formatDate works', () => {
    expect(formatDate('2026-03-07 07:08:20 +0000')).toBe('2026-03-07');
    expect(formatDate('')).toBe('');
  });

  it('formatCount works', () => {
    expect(formatCount(22979)).toBe('22,979');
  });
});



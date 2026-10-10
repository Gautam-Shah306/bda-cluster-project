import { render, screen } from '@testing-library/react';
import SkillsIntelligence from './SkillsIntelligence';
import { setupMockApi, restoreMockApi, overrideMock } from '../../testing/mockApi';
import { expect, test, beforeEach, afterEach, describe } from 'vitest';

describe('SkillsIntelligence', () => {
  beforeEach(() => setupMockApi());
  afterEach(() => restoreMockApi());

  test('displays rising and declining skills and gap map', async () => {
    overrideMock('/dashboard/skill-trends', {
      status: 200,
      body: {
        rising_skills: [{ name: 'python', growth: '+10', color: 'green' }],
        declining_skills: [{ name: 'java', decline: '-5', color: 'red' }]
      }
    });

    render(<SkillsIntelligence />);
    
    expect(await screen.findByText('Python')).toBeInTheDocument();
    expect(await screen.findByText('+10')).toBeInTheDocument();
    
    expect(screen.getByText('Java')).toBeInTheDocument();
    expect(screen.getByText('-5')).toBeInTheDocument();
    
    expect(screen.getByText('Market Skill Gap Map')).toBeInTheDocument();
  });

  test('empty gap text', async () => {
    overrideMock('/dashboard/skill-gap', { status: 200, body: [] });
    render(<SkillsIntelligence />);
    
    expect(await screen.findByText('No skill gap data available.')).toBeInTheDocument();
  });
});





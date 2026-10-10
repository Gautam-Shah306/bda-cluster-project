import { render, screen, waitFor } from '@testing-library/react';
import HiringTrends from './HiringTrends';
import { setupMockApi, restoreMockApi, recordedCalls } from '../../testing/mockApi';
import { expect, test, beforeEach, afterEach, describe } from 'vitest';

describe('HiringTrends', () => {
  beforeEach(() => setupMockApi());
  afterEach(() => restoreMockApi());

  test('displays titles and estimated active roles', async () => {
    render(<HiringTrends />);
    
    expect(await screen.findByText('Aggregate Job Postings')).toBeInTheDocument();
    expect(screen.getByText('City Demand Comparison')).toBeInTheDocument();
    expect(screen.getByText('Postings (left axis) and Estimated Active Roles (right axis, 0.8 x postings)')).toBeInTheDocument();
    
    await waitFor(() => {
      const hiringCalls = recordedCalls.filter(c => c.url.includes('/dashboard/hiring-trends'));
      const citiesCalls = recordedCalls.filter(c => c.url.includes('/dashboard/top-cities'));
      expect(hiringCalls.length).toBe(1);
      expect(citiesCalls.length).toBe(1);
    });
  });
});




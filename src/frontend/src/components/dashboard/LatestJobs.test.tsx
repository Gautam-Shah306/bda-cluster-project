import { render, screen, waitFor } from '@testing-library/react';
import LatestJobs from './LatestJobs';
import { setupMockApi, restoreMockApi, overrideMock } from '../../testing/mockApi';
import { expect, test, beforeEach, afterEach, describe } from 'vitest';

describe('LatestJobs', () => {
  beforeEach(() => setupMockApi());
  afterEach(() => restoreMockApi());

  test('renders rows correctly with fallbacks', async () => {
    overrideMock('/dashboard/latest-jobs', {
      status: 200,
      body: [
        { jobtitle: 'Dev', company: 'Corp', location: '', skills: 'react', experience: '', postdate: '2026-03-07 07:08:20 +0000' },
        { jobtitle: 'Designer', company: 'Art', location: 'Remote', skills: 'css', experience: '1 yr', postdate: '2026-03-08 12:00:00 +0000' }
      ]
    });

    render(<LatestJobs refreshTrigger={0} />);
    
    await waitFor(() => {
      expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
    });

    const rows = screen.getAllByRole('row');
    expect(rows.length).toBe(3); // 1 header + 2 data

    expect(screen.getByText('2026-03-07')).toBeInTheDocument();
    expect(screen.getByText('N/A')).toBeInTheDocument();
    expect(screen.getByText('Unknown')).toBeInTheDocument();
  });

  test('empty state text', async () => {
    overrideMock('/dashboard/latest-jobs', { status: 200, body: [] });
    render(<LatestJobs refreshTrigger={0} />);
    
    expect(await screen.findByText('No scraped jobs available yet')).toBeInTheDocument();
  });
});



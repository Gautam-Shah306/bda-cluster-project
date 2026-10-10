import { render, screen } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from '../../context';
import { expect, test, beforeEach, afterEach, describe, vi, type MockInstance } from 'vitest';
import { setupMockApi, restoreMockApi, recordedCalls } from '../../testing/mockApi';

import Overview from './Overview';
import HiringTrends from './HiringTrends';
import SkillsIntelligence from './SkillsIntelligence';
import AIVulnerability from './AIVulnerability';

const renderWithProviders = (ui: React.ReactElement) => {
  return render(
    <AuthProvider>
      <MemoryRouter>
        {ui}
      </MemoryRouter>
    </AuthProvider>
  );
};

describe('Dashboard Pages Contract', () => {
  let consoleErrorSpy: MockInstance;

  beforeEach(() => {
    localStorage.clear();
    localStorage.setItem('token', 'test-token');
    localStorage.setItem('user', JSON.stringify({ name: 'Bob', email: 'b@b.com' }));
    setupMockApi();
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    restoreMockApi();
    consoleErrorSpy.mockRestore();
  });

  const checkPage = async (
    ui: React.ReactElement,
    expectedTitles: string[],
  ) => {
    recordedCalls.length = 0; // clear recorded calls
    renderWithProviders(ui);

    for (const title of expectedTitles) {
      expect(await screen.findByText(title)).toBeInTheDocument();
    }

    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(consoleErrorSpy).not.toHaveBeenCalled();

    // Verify fetches
    expect(recordedCalls.length).toBeGreaterThan(0);
    // Note: Since mockApi doesn't currently record status in recordedCalls, 
    // we can only verify that fetches were made and no errors were thrown.
    // The fact that titles rendered means data was successfully loaded.
  };

  test('Overview renders successfully', async () => {
    await checkPage(<Overview />, ['Dashboard', 'Hiring Trends Over Time']);
  });

  test('HiringTrends renders successfully', async () => {
    await checkPage(<HiringTrends />, ['Aggregate Job Postings']);
  });

  test('SkillsIntelligence renders successfully', async () => {
    await checkPage(<SkillsIntelligence />, ['Market Skill Gap Map']);
  });

  test('AIVulnerability renders successfully', async () => {
    await checkPage(<AIVulnerability />, ['Risk Assessment Table']);
  });
});

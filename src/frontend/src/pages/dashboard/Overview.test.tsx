import { render, screen, act, fireEvent, waitFor } from '@testing-library/react';
import Overview from './Overview';
import { setupMockApi, restoreMockApi, recordedCalls, overrideMock } from '../../testing/mockApi';
import { expect, test, beforeEach, afterEach, describe, vi, type MockInstance } from 'vitest';

describe('Overview', () => {
  let consoleErrorSpy: MockInstance;

  beforeEach(() => {
    setupMockApi();
    consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    restoreMockApi();
    consoleErrorSpy.mockRestore();
  });

  test('loads and displays stats and trends without console errors', async () => {
    render(<Overview />);
    
    // the 4 stat values appear
    expect(await screen.findByText('22,979')).toBeInTheDocument();
    expect(screen.getAllByText('Business Development Executive').length).toBeGreaterThan(0);
    expect(screen.getAllByText('Bengaluru/Bangalore').length).toBeGreaterThan(0);
    expect(screen.getByText('Sales')).toBeInTheDocument();

    // the select has the options
    const select = await screen.findByLabelText('Skills year') as HTMLSelectElement;
    expect(select.options.length).toBe(5);
    const options = Array.from(select.options).map(o => o.value);
    expect(options).toEqual(['all', '2026', '2017', '2016', '2015']);
    
    // 2026 selected
    expect(select.value).toBe('2026');
    
    await waitFor(() => {
      const trendCalls = recordedCalls.filter(c => c.url.includes('/dashboard/skill-trends'));
      expect(trendCalls.length).toBe(1);
      expect(trendCalls[0].url).toMatch(/\?year=2026$/);
    });
    
    // choosing "All years" issues /dashboard/skill-trends without a year
    act(() => {
      fireEvent.change(select, { target: { value: 'all' } });
    });
    
    await waitFor(() => {
      const allYearsCall = recordedCalls.filter(c => c.url.includes('/dashboard/skill-trends')).pop();
      expect(allYearsCall?.url).not.toContain('?year=');
    });

    // choosing "2017" issues /dashboard/skill-trends with a year
    act(() => {
      fireEvent.change(select, { target: { value: '2017' } });
    });
    
    await waitFor(() => {
      const trendCalls = recordedCalls.filter(c => c.url.includes('/dashboard/skill-trends'));
      expect(trendCalls.pop()?.url).toMatch(/\?year=2017$/);
    });

    expect(consoleErrorSpy).not.toHaveBeenCalled();
  });

  test('Refresh Data issues second request to every endpoint', async () => {
    render(<Overview />);
    await screen.findByText('22,979');
    
    const initialCalls = recordedCalls.length;
    
    const refreshBtn = screen.getByRole('button', { name: /Refresh Data/i });
    act(() => {
      fireEvent.click(refreshBtn);
    });
    
    expect(recordedCalls.length).toBeGreaterThan(initialCalls);
  });

  test('a years request returning the bare array shows role="alert" while the rest of the page still renders', async () => {
    overrideMock('/dashboard/skill-trend-years', { status: 200, body: [2026, 2017] });
    
    render(<Overview />);
    
    const alert = await screen.findByRole('alert');
    expect(alert).toHaveTextContent('Unexpected response from /dashboard/skill-trend-years');
    
    expect(await screen.findByText('22,979')).toBeInTheDocument();
    expect(screen.getByText('Hiring Trends Over Time')).toBeInTheDocument();
  });
});

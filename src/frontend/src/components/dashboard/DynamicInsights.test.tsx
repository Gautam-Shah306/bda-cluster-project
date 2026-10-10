import { render, screen, waitFor } from '@testing-library/react';
import DynamicInsights from './DynamicInsights';
import { setupMockApi, restoreMockApi, recordedCalls, overrideMock } from '../../testing/mockApi';
import { expect, test, beforeEach, afterEach, describe } from 'vitest';

describe('DynamicInsights', () => {
  beforeEach(() => setupMockApi());
  afterEach(() => restoreMockApi());

  test('defaults to first city and role, requests data, changes update requests', async () => {
    overrideMock('/dashboard/top-cities', { status: 200, body: [{ name: 'Bengaluru', demand: 100 }, { name: 'Pune', demand: 50 }] });
    overrideMock('/dashboard/top-roles', { status: 200, body: [{ role: 'Developer', count: 50 }, { role: 'Tester', count: 20 }] });
    
    render(<DynamicInsights refreshTrigger={0} />);
    
    // Wait for selects to populate
    const citySelect = await screen.findByLabelText('City') as HTMLSelectElement;
    const roleSelect = await screen.findByLabelText('Role') as HTMLSelectElement;
    
    await waitFor(() => {
      expect(citySelect.value).toBe('Bengaluru');
      expect(roleSelect.value).toBe('Developer');
    });

    const distCall = recordedCalls.find(c => c.url.includes('/dashboard/city-role-distribution'));
    expect(distCall?.url).toContain('?city=Bengaluru');

    const spreadCall = recordedCalls.find(c => c.url.includes('/dashboard/role-city-distribution'));
    expect(spreadCall?.url).toContain('?role=Developer');

  });

  test('empty state texts', async () => {
    overrideMock('/dashboard/top-cities', { status: 200, body: [{ name: 'Bengaluru', demand: 100 }] });
    overrideMock('/dashboard/top-roles', { status: 200, body: [{ role: 'Developer', count: 50 }] });
    overrideMock('/dashboard/city-role-distribution', { status: 200, body: [] });
    overrideMock('/dashboard/role-city-distribution', { status: 200, body: [] });
    
    render(<DynamicInsights refreshTrigger={0} />);
    await waitFor(() => {
      expect(screen.getByText('No roles found for this city.')).toBeInTheDocument();
      expect(screen.getByText('No cities found for this role.')).toBeInTheDocument();
    }, { timeout: 2000 });
  });
});





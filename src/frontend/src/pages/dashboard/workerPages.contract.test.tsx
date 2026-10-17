import { render, screen } from '@testing-library/react';
import { expect, test, beforeEach, afterEach, describe, vi, type MockInstance } from 'vitest';
import { setupMockApi, restoreMockApi, overrideMock } from '../../testing/mockApi';
import { contractSavedProfile, contractReskillingPlan } from '../../testing/liveFixtures';
import WorkerIntelligence from './WorkerIntelligence';
import ReskillingPath from './ReskillingPath';
import Chatbot from './Chatbot';

describe('Worker pages contract (contract-derived fixtures, see liveFixtures.ts)', () => {
  let errSpy: MockInstance;
  beforeEach(() => {
    localStorage.clear();
    setupMockApi();
    errSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });
  afterEach(() => {
    errSpy.mockRestore();
    restoreMockApi();
  });

  test('WorkerIntelligence with a saved profile', async () => {
    overrideMock('GET /worker/profile', { status: 200, body: contractSavedProfile });
    render(<WorkerIntelligence />);
    expect(await screen.findByText('78/100')).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(errSpy).not.toHaveBeenCalled();
  });

  test('WorkerIntelligence for a brand-new user', async () => {
    render(<WorkerIntelligence />);
    expect(await screen.findByText('Worker Analysis')).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(errSpy).not.toHaveBeenCalled();
  });

  test('ReskillingPath with a stored plan', async () => {
    overrideMock('GET /worker/reskilling', { status: 200, body: contractReskillingPlan });
    render(<ReskillingPath />);
    expect(await screen.findByText('Learning Timeline')).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(errSpy).not.toHaveBeenCalled();
  });

  test('Chatbot renders', () => {
    render(<Chatbot />);
    expect(screen.getByRole('heading', { name: 'AI Chatbot' })).toBeInTheDocument();
    expect(screen.queryByRole('alert')).not.toBeInTheDocument();
    expect(errSpy).not.toHaveBeenCalled();
  });
});

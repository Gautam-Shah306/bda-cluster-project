import { render, screen, waitFor, fireEvent, cleanup } from '@testing-library/react';
import WorkerIntelligence from './WorkerIntelligence';
import { setupMockApi, restoreMockApi, recordedCalls, overrideMock } from '../../testing/mockApi';
import { contractSavedProfile } from '../../testing/liveFixtures';
import { expect, test, beforeEach, afterEach, describe } from 'vitest';

const analysis = (score: unknown, extra: Record<string, unknown> = {}) => ({
  parsed_profile: {},
  gemini_analysis: { risk_score: score, risk_level: 'high', pivot_roles: ['Data Analyst'], new_skills: ['SQL'], explanation: 'Because.', ...extra },
});

async function fillAndSubmit() {
  fireEvent.change(screen.getByLabelText(/current job title/i), { target: { value: 'Agent' } });
  fireEvent.change(screen.getByLabelText(/^city/i), { target: { value: 'Pune' } });
  fireEvent.change(screen.getByLabelText(/years of experience/i), { target: { value: '2.5' } });
  fireEvent.change(screen.getByLabelText(/day to day/i), { target: { value: 'Calls' } });
  fireEvent.change(screen.getByLabelText(/skills/i), { target: { value: 'crm, , excel ' } });
  fireEvent.click(screen.getByRole('button', { name: /analyze risk/i }));
}

describe('WorkerIntelligence', () => {
  beforeEach(() => {
    localStorage.clear();
    setupMockApi();
  });
  afterEach(() => {
    cleanup();
    restoreMockApi();
  });

  test('draft is saved on change and kept when the profile has no job role', async () => {
    localStorage.setItem('worker_form_draft', JSON.stringify({ title: 'Old', city: 'X', experience: '1', description: 'd', skills: '' }));
    render(<WorkerIntelligence />);
    await waitFor(() => expect(recordedCalls.some((c) => c.url.includes('/worker/profile'))).toBe(true));
    expect((screen.getByLabelText(/current job title/i) as HTMLInputElement).value).toBe('Old');
    fireEvent.change(screen.getByLabelText(/^city/i), { target: { value: 'Delhi' } });
    await waitFor(() => expect(JSON.parse(localStorage.getItem('worker_form_draft') as string).city).toBe('Delhi'));
  });

  test('a saved backend profile replaces the draft and shows its analysis', async () => {
    localStorage.setItem('worker_form_draft', JSON.stringify({ title: 'Old', city: '', experience: '', description: '', skills: '' }));
    overrideMock('GET /worker/profile', { status: 200, body: contractSavedProfile });
    render(<WorkerIntelligence />);
    await waitFor(() => expect((screen.getByLabelText(/current job title/i) as HTMLInputElement).value).toBe('BPO Voice Executive'));
    expect((screen.getByLabelText(/years of experience/i) as HTMLInputElement).value).toBe('3');
    expect((screen.getByLabelText(/skills/i) as HTMLInputElement).value).toBe('communication, crm');
    expect(await screen.findByText('78/100')).toBeInTheDocument();
    expect(screen.getByText('AI Content Moderation Analyst')).toBeInTheDocument();
  });

  test('submit sends the exact payload', async () => {
    overrideMock('POST /worker/profile', { status: 200, body: analysis(70) });
    render(<WorkerIntelligence />);
    await fillAndSubmit();
    expect(await screen.findByText('70/100')).toBeInTheDocument();
    const post = recordedCalls.find((c) => c.method === 'POST' && c.url.endsWith('/worker/profile'));
    expect(post?.body).toEqual({ job_role: 'Agent', city: 'Pune', years_of_experience: 2.5, role_description: 'Calls', skills: ['crm', 'excel'] });
  });

  test('banner appears at 86 and not at 85', async () => {
    overrideMock('POST /worker/profile', { status: 200, body: analysis(85) });
    render(<WorkerIntelligence />);
    await fillAndSubmit();
    await screen.findByText('85/100');
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
    cleanup();

    overrideMock('POST /worker/profile', { status: 200, body: analysis(86) });
    render(<WorkerIntelligence />);
    await fillAndSubmit();
    await screen.findByText('86/100');
    expect(screen.getByRole('status')).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /dismiss/i }));
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  test.each([[null], ['abc']])('score %s shows "Score unavailable" and still the explanation', async (score) => {
    overrideMock('POST /worker/profile', { status: 200, body: analysis(score) });
    render(<WorkerIntelligence />);
    await fillAndSubmit();
    expect(await screen.findByText('Score unavailable')).toBeInTheDocument();
    expect(screen.getByText('Because.')).toBeInTheDocument();
    expect(screen.queryByTestId('risk-bar')).not.toBeInTheDocument();
  });

  test('score 150 shows the rounded label but a bar clamped to 100%', async () => {
    overrideMock('POST /worker/profile', { status: 200, body: analysis(150) });
    render(<WorkerIntelligence />);
    await fillAndSubmit();
    expect(await screen.findByText('150/100')).toBeInTheDocument();
    expect(screen.getByTestId('risk-bar')).toHaveStyle({ width: '100%' });
  });

  test('an API error shows role="alert"', async () => {
    overrideMock('POST /worker/profile', { status: 500, body: { detail: 'Boom' } });
    render(<WorkerIntelligence />);
    await fillAndSubmit();
    expect(await screen.findByRole('alert')).toHaveTextContent('Boom');
  });

  test('the methodology formula is shown', () => {
    render(<WorkerIntelligence />);
    expect(screen.getByText(/Automation Probability x 0\.4/)).toBeInTheDocument();
  });
});

import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import ReskillingPath from './ReskillingPath';
import { setupMockApi, restoreMockApi, recordedCalls, overrideMock } from '../../testing/mockApi';
import { contractReskillingPlan } from '../../testing/liveFixtures';
import { expect, test, beforeEach, afterEach, describe, vi, type MockInstance } from 'vitest';

describe('ReskillingPath', () => {
  let errSpy: MockInstance;
  beforeEach(() => {
    setupMockApi();
    errSpy = vi.spyOn(console, 'error').mockImplementation(() => {});
  });
  afterEach(() => {
    cleanup();
    errSpy.mockRestore();
    restoreMockApi();
  });

  test('no plan: only the Generate button and a hint', async () => {
    render(<ReskillingPath />);
    expect(await screen.findByText(/No plan yet/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Generate Path' })).toBeInTheDocument();
    expect(screen.queryByText('Learning Timeline')).not.toBeInTheDocument();
  });

  test('stored plan shows every section and the button reads Regenerate', async () => {
    overrideMock('GET /worker/reskilling', { status: 200, body: contractReskillingPlan });
    render(<ReskillingPath />);
    expect(await screen.findByText('Move from scripted voice support towards data work.')).toBeInTheDocument();
    for (const t of ['Recommended Skills', 'Learning Timeline', 'Recommended Courses', 'Recommended Jobs']) {
      expect(screen.getByText(t)).toBeInTheDocument();
    }
    expect(screen.getByText('Start Here')).toBeInTheDocument();
    expect(screen.getByLabelText('Final step')).toBeInTheDocument();
    expect(screen.getByText('12 weeks')).toBeInTheDocument();
    const open = screen.getByRole('link', { name: 'Open' });
    expect(open).toHaveAttribute('rel', 'noopener noreferrer');
    expect(screen.getByRole('button', { name: 'Regenerate Path' })).toBeInTheDocument();
  });

  test('generating posts with no body and shows the plan', async () => {
    render(<ReskillingPath />);
    fireEvent.click(await screen.findByRole('button', { name: 'Generate Path' }));
    expect(await screen.findByText('Move from scripted voice support towards data work.')).toBeInTheDocument();
    const post = recordedCalls.find((c) => c.method === 'POST');
    expect(post?.url).toMatch(/\/worker\/reskilling$/);
    expect(post?.body).toBeUndefined();
    expect(screen.getByRole('button', { name: 'Regenerate Path' })).toBeInTheDocument();
  });

  test('an error string in the response is shown in an alert', async () => {
    overrideMock('POST /worker/reskilling', {
      status: 200,
      body: { recommendation_type: null, summary: 'x', error: 'Gemini request failed: boom' },
    });
    render(<ReskillingPath />);
    fireEvent.click(await screen.findByRole('button', { name: 'Generate Path' }));
    expect(await screen.findByRole('alert')).toHaveTextContent('Gemini request failed: boom');
  });

  test('a javascript: course URL renders no Open link', async () => {
    overrideMock('GET /worker/reskilling', {
      status: 200,
      body: { ...contractReskillingPlan, recommended_courses: [{ name: 'Bad', url: 'javascript:alert(1)' }] },
    });
    render(<ReskillingPath />);
    expect(await screen.findByText('Bad')).toBeInTheDocument();
    expect(screen.queryByRole('link', { name: 'Open' })).not.toBeInTheDocument();
  });

  test('a malformed plan renders without console.error', async () => {
    overrideMock('GET /worker/reskilling', {
      status: 200,
      body: {
        recommendation_type: 'upskilling',
        summary: 42,
        recommended_skills: null,
        recommended_courses: [null, {}, 'x'],
        recommended_jobs: [{ title: 'T' }],
        learning_path: [{}, { week: 'W' }],
      },
    });
    render(<ReskillingPath />);
    expect(await screen.findByText('Recommended Jobs')).toBeInTheDocument();
    expect(screen.getByText('T')).toBeInTheDocument();
    expect(errSpy).not.toHaveBeenCalled();
  });
});

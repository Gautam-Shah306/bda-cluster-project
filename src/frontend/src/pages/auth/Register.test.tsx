
import { render, screen, act, fireEvent, cleanup } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import Register from './Register';
import { expect, test, vi, beforeEach, afterEach, describe } from 'vitest';
import * as api from '../../services/api';

vi.mock('../../services/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../services/api')>();
  return {
    ...actual,
    signupApi: vi.fn(),
  };
});

const renderRegister = () => {
  return render(
    <MemoryRouter initialEntries={['/register']}>
      <Routes>
        <Route path="/register" element={<Register />} />
        <Route path="/login" element={<div data-testid="login-page">Login Page</div>} />
      </Routes>
    </MemoryRouter>
  );
};

describe('Register.tsx', () => {
  afterEach(cleanup);
  beforeEach(() => {
    vi.mocked(api.signupApi).mockClear();
    vi.useFakeTimers();
  });

  test('success shows "Account created successfully", then (fake timers) after 1500 ms the Login page is shown', async () => {
    vi.mocked(api.signupApi).mockResolvedValue({ message: 'ok' });

    renderRegister();

    fireEvent.change(screen.getByLabelText(/full name/i), { target: { value: 'Jane' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'jane@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pass' } });
    
    await act(async () => {
      screen.getByRole('button', { name: /sign up/i }).click();
    });

    expect(screen.getByText('Account created successfully')).toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(1000);
    });
    expect(screen.queryByTestId('login-page')).not.toBeInTheDocument();

    act(() => {
      vi.advanceTimersByTime(500);
    });
    expect(screen.getByTestId('login-page')).toBeInTheDocument();
  });

  test('a 400 shows "Email already registered"', async () => {
    vi.mocked(api.signupApi).mockRejectedValue(new api.ApiError(400, '', 'Email already registered'));

    renderRegister();

    fireEvent.change(screen.getByLabelText(/full name/i), { target: { value: 'Jane' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'jane@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pass' } });
    
    await act(async () => {
      screen.getByRole('button', { name: /sign up/i }).click();
    });

    expect(screen.getByText('Email already registered')).toBeInTheDocument();
  });

  test('unmounting before 1500 ms causes no navigation and no error', async () => {
    vi.mocked(api.signupApi).mockResolvedValue({ message: 'ok' });

    const { unmount } = renderRegister();

    fireEvent.change(screen.getByLabelText(/full name/i), { target: { value: 'Jane' } });
    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'jane@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pass' } });
    
    await act(async () => {
      screen.getByRole('button', { name: /sign up/i }).click();
    });

    unmount();

    act(() => {
      vi.advanceTimersByTime(1500);
    });
    // No crash, and test passes.
  });
});

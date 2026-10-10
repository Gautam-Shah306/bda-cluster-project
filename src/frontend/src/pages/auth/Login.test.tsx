
import { render, screen, act, fireEvent, cleanup } from '@testing-library/react';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { AuthProvider } from '../../context';
import Login from './Login';
import { expect, test, beforeEach, afterEach, describe } from 'vitest';
import * as api from '../../services/api';

vi.mock('../../services/api', async (importOriginal) => {
  const actual = await importOriginal<typeof import('../../services/api')>();
  return {
    ...actual,
    loginApi: vi.fn(),
  };
});

const renderLogin = () => {
  return render(
    <AuthProvider>
      <MemoryRouter initialEntries={['/login']}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/dashboard" element={<div data-testid="dashboard">Dashboard Shell</div>} />
        </Routes>
      </MemoryRouter>
    </AuthProvider>
  );
};

describe('Login.tsx', () => {
  afterEach(cleanup);
  beforeEach(() => {
    localStorage.clear();
    vi.mocked(api.loginApi).mockClear();
  });

  test('success (fetch mocked) -> localStorage "token" is set, "user" equals {name: "jane", email: "jane@example.com"} for that email, and the dashboard shell is shown; the button reads "Authenticating..." while pending', async () => {
    let resolveLogin: (val: { access_token: string, token_type: string }) => void = () => {};
    const loginPromise = new Promise<{ access_token: string, token_type: string }>((res) => {
      resolveLogin = res;
    });
    vi.mocked(api.loginApi).mockReturnValue(loginPromise);

    renderLogin();

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'jane@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pass' } });
    
    const submitBtn = screen.getByRole('button', { name: /sign in/i });
    
    act(() => {
      submitBtn.click();
    });

    expect(submitBtn.textContent).toBe('Authenticating...');

    await act(async () => {
      resolveLogin({ access_token: 'valid-token', token_type: 'bearer' });
    });

    expect(localStorage.getItem('token')).toBe('valid-token');
    expect(localStorage.getItem('user')).toBe(JSON.stringify({ name: 'jane', email: 'jane@example.com' }));
    expect(screen.getByTestId('dashboard')).toBeInTheDocument();
  });

  test('a 401 shows "Invalid credentials" and stores nothing', async () => {
    vi.mocked(api.loginApi).mockRejectedValue(new api.ApiError(401, '', 'Invalid credentials'));

    renderLogin();

    fireEvent.change(screen.getByLabelText(/email/i), { target: { value: 'jane@example.com' } });
    fireEvent.change(screen.getByLabelText(/password/i), { target: { value: 'pass' } });
    
    const submitBtn = screen.getByRole('button', { name: /sign in/i });
    
    await act(async () => {
      submitBtn.click();
    });

    expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    expect(localStorage.getItem('token')).toBeNull();
  });
});



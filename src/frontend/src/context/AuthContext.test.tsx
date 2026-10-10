import { render, screen, act, cleanup } from '@testing-library/react';
import { AuthProvider } from './AuthProvider';
import { useAuth } from './useAuth';
import { expect, test, beforeEach, afterEach, describe } from 'vitest';

const TestComponent = ({ onRender }: { onRender?: (isAuthenticated: boolean) => void }) => {
  const { isAuthenticated, user, login, logout } = useAuth();
  
  if (onRender) {
    onRender(isAuthenticated);
  }

  return (
    <div>
      <div data-testid="auth-status">{isAuthenticated ? 'yes' : 'no'}</div>
      <div data-testid="user-name">{user?.name}</div>
      <button onClick={() => login('new_token', { name: 'alice', email: 'alice@a.com' })} data-testid="login-btn">Login</button>
      <button onClick={logout} data-testid="logout-btn">Logout</button>
    </div>
  );
};

describe('AuthContext', () => {
  afterEach(cleanup);
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  test('token+user in storage -> signed in on the FIRST render', () => {
    localStorage.setItem('token', 'fake-token');
    localStorage.setItem('user', JSON.stringify({ name: 'Bob', email: 'bob@example.com' }));
    
    const renders: boolean[] = [];
    
    render(
      <AuthProvider>
        <TestComponent onRender={(isAuth) => renders.push(isAuth)} />
      </AuthProvider>
    );

    // console.log('RENDERS ARRAY:', renders);
    expect(renders.length).toBeGreaterThan(0);
    expect(renders).not.toContain(false);
    expect(screen.getByTestId('auth-status').textContent).toBe('yes');
    expect(screen.getByTestId('user-name').textContent).toBe('Bob');
  });

  test('user without token -> signed out', () => {
    localStorage.setItem('user', JSON.stringify({ name: 'Bob', email: 'bob@example.com' }));
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('auth-status').textContent).toBe('no');
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  test('token without user -> signed out', () => {
    localStorage.setItem('token', 'fake-token');
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('auth-status').textContent).toBe('no');
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  test('corrupt user JSON -> signed out and both keys removed', () => {
    localStorage.setItem('token', 'fake-token');
    localStorage.setItem('user', '{bad-json');
    
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );

    expect(screen.getByTestId('auth-status').textContent).toBe('no');
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  test('login() stores both keys and updates state; logout() removes both and clears state', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    expect(screen.getByTestId('auth-status').textContent).toBe('no');
    
    act(() => {
      screen.getByTestId('login-btn').click();
    });
    
    expect(screen.getByTestId('auth-status').textContent).toBe('yes');
    expect(localStorage.getItem('token')).toBe('new_token');
    expect(localStorage.getItem('user')).toBe(JSON.stringify({ name: 'alice', email: 'alice@a.com' }));
    
    act(() => {
      screen.getByTestId('logout-btn').click();
    });
    
    expect(screen.getByTestId('auth-status').textContent).toBe('no');
    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
  });

  test('useAuth outside the provider throws', () => {
    const consoleError = vi.spyOn(console, 'error').mockImplementation(() => {});
    
    const BadComponent = () => {
      useAuth();
      return null;
    };
    
    expect(() => render(<BadComponent />)).toThrow('useAuth must be used within an AuthProvider');
    
    consoleError.mockRestore();
  });
});



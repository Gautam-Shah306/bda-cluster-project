
import { render, screen, act, cleanup } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { AuthProvider } from './context';
import { AppRoutes } from './App';
import { expect, test, vi, beforeEach, afterEach, describe } from 'vitest';

const renderApp = (initialRoute: string) => {
  return render(
    <AuthProvider>
      <MemoryRouter initialEntries={[initialRoute]}>
        <AppRoutes />
      </MemoryRouter>
    </AuthProvider>
  );
};

describe('App routing', () => {
  afterEach(cleanup);
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  test('signed out at /dashboard -> the Login page', () => {
    renderApp('/dashboard');
    expect(screen.getByText('Welcome Back')).toBeInTheDocument();
  });

  test('signed out at /dashboard/worker -> the Login page', () => {
    renderApp('/dashboard/worker');
    expect(screen.getByText('Welcome Back')).toBeInTheDocument();
  });

  test('storage set BEFORE rendering at /dashboard (simulated hard refresh) -> the dashboard shell stays (no redirect), showing the groups "Core Intelligence" and "Worker Action" and 7 navigation links', () => {
    localStorage.setItem('token', 't');
    localStorage.setItem('user', JSON.stringify({ name: 'Bob', email: 'b@b.com' }));
    
    renderApp('/dashboard');
    
    expect(screen.getByText('Core Intelligence')).toBeInTheDocument();
    expect(screen.getByText('Worker Action')).toBeInTheDocument();
    expect(screen.queryByRole('heading', { name: /Welcome Back/i })).toBeNull();
    
    const nav = screen.getByRole('navigation');
    const links = Array.from(nav.querySelectorAll('a'));
    expect(links).toHaveLength(7);

    const expected = [
      { text: 'Dashboard', href: '/dashboard' },
      { text: 'Hiring Trends', href: '/dashboard/hiring-trends' },
      { text: 'Skills Intelligence', href: '/dashboard/skills' },
      { text: 'AI Vulnerability Index', href: '/dashboard/vulnerability' },
      { text: 'Worker Analysis', href: '/dashboard/worker' },
      { text: 'Reskilling Paths', href: '/dashboard/reskilling' },
      { text: 'AI Chatbot', href: '/dashboard/chatbot' }
    ];

    expected.forEach((exp, i) => {
      expect(links[i].textContent).toContain(exp.text);
      expect(links[i].getAttribute('href')).toBe(exp.href);
    });
  });

  test('signed in at /dashboard/chatbot -> the Chatbot placeholder title', () => {
    localStorage.setItem('token', 't');
    localStorage.setItem('user', JSON.stringify({ name: 'Bob', email: 'b@b.com' }));
    
    renderApp('/dashboard/chatbot');
    // From Chatbot component
    expect(screen.getByRole('heading', { name: 'AI Chatbot' })).toBeInTheDocument();
  });

  test('an unknown path -> NotFound', () => {
    renderApp('/this-does-not-exist');
    expect(screen.getByText('404')).toBeInTheDocument();
    expect(screen.getByText('Page Not Found')).toBeInTheDocument();
  });

  test('Landing shows Login and Sign Up when signed out and "Go to Dashboard" when signed in', () => {
    const { unmount } = renderApp('/');
    expect(screen.getByRole('link', { name: /login/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /sign up/i })).toBeInTheDocument();
    
    unmount();
    localStorage.setItem('token', 't');
    localStorage.setItem('user', JSON.stringify({ name: 'Bob', email: 'b@b.com' }));
    
    renderApp('/');
    expect(screen.getByRole('link', { name: /go to dashboard/i })).toBeInTheDocument();
  });

  test('clicking logout on the dashboard returns to the Login page', () => {
    localStorage.setItem('token', 't');
    localStorage.setItem('user', JSON.stringify({ name: 'Bob', email: 'b@b.com' }));
    
    renderApp('/dashboard');
    
    const logoutBtn = screen.getByRole('button', { name: /logout/i });
    act(() => {
      logoutBtn.click();
    });
    
    expect(screen.getByText('Welcome Back')).toBeInTheDocument();
  });
});

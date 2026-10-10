
import { render, screen, act, cleanup } from '@testing-library/react';
import { MemoryRouter, Routes, Route } from 'react-router-dom';
import DashboardLayout from './layout/DashboardLayout';
import { AuthProvider } from './context';
import { AppRoutes } from './App';
import { expect, test, beforeEach, afterEach, describe } from 'vitest';
import { setupMockApi, restoreMockApi } from './testing/mockApi';

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
    setupMockApi();
    vi.restoreAllMocks();
    restoreMockApi();
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

    test('signed in at /dashboard/hiring-trends -> shows the title "Aggregate Job Postings"', async () => {
    localStorage.setItem('token', 't');
    localStorage.setItem('user', JSON.stringify({ name: 'Bob', email: 'b@b.com' }));
    
    renderApp('/dashboard/hiring-trends');
    expect(await screen.findByText('Aggregate Job Postings')).toBeInTheDocument();
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

  test('a signed-in user at /dashboard with a page that throws shows the alert AND the sidebar links', () => {
    localStorage.setItem('token', 't');
    localStorage.setItem('user', JSON.stringify({ name: 'Bob', email: 'b@b.com' }));
    
    const ThrowingComponent = () => {
      throw new Error('Test crash');
    };

    // Spy on console.error to avoid noise
    const consoleErrorSpy = vi.spyOn(console, 'error').mockImplementation(() => {});

    render(
      <AuthProvider>
        <MemoryRouter initialEntries={['/dashboard/crash']}>
          <Routes>
            <Route element={<DashboardLayout />}>
              <Route path="/dashboard/crash" element={<ThrowingComponent />} />
            </Route>
          </Routes>
        </MemoryRouter>
      </AuthProvider>
    );

    expect(screen.getByRole('alert')).toBeInTheDocument();
    expect(screen.getByText('Something went wrong while showing this page.')).toBeInTheDocument();
    expect(screen.getByText('Test crash')).toBeInTheDocument();
    expect(screen.getByText('Core Intelligence')).toBeInTheDocument();

    consoleErrorSpy.mockRestore();
  });
});




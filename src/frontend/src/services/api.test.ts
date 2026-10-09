import { expect, test, vi, beforeEach, describe } from 'vitest';
import { apiFetch, loginApi, signupApi, setUnauthorizedHandler, ApiError, API_BASE } from './api';

const mockFetch = vi.fn();
globalThis.fetch = mockFetch as unknown as typeof fetch;

describe('api.ts', () => {
  // afterEach removed
  beforeEach(() => {
    localStorage.clear();
    mockFetch.mockClear();
    setUnauthorizedHandler(null);
  });

  test('login/signup send no Authorization header even when a token is stored', async () => {
    localStorage.setItem('token', 'secret');
    mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });
    await loginApi({ email: 'a@a.com', password: '123' });
    expect(mockFetch.mock.calls[0][1].headers.Authorization).toBeUndefined();

    mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });
    await signupApi({ name: 'A', email: 'a@a.com', password: '123' });
    expect(mockFetch.mock.calls[1][1].headers.Authorization).toBeUndefined();
  });

  test('another call with auth true attaches "Bearer <token>"', async () => {
    localStorage.setItem('token', 'my-token');
    mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });
    await apiFetch('/test');
    expect(mockFetch.mock.calls[0][1].headers.Authorization).toBe('Bearer my-token');
  });

  test('a JSON body sets Content-Type', async () => {
    mockFetch.mockResolvedValueOnce({ ok: true, json: async () => ({}) });
    await apiFetch('/test', { body: { data: 1 } });
    expect(mockFetch.mock.calls[0][1].headers['Content-Type']).toBe('application/json');
  });

  test('401 with a token -> storage cleared, handler called exactly once, ApiError.status 401', async () => {
    localStorage.setItem('token', 'bad-token');
    localStorage.setItem('user', 'u');
    const handler = vi.fn();
    setUnauthorizedHandler(handler);

    mockFetch.mockResolvedValueOnce({ 
      ok: false, 
      status: 401, 
      json: async () => ({ detail: 'Token expired' }) 
    });

    try {
      await apiFetch('/protected');
      expect.fail('Should throw');
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      if (e instanceof ApiError) {
        expect(e.status).toBe(401);
      }
    }

    expect(localStorage.getItem('token')).toBeNull();
    expect(localStorage.getItem('user')).toBeNull();
    expect(handler).toHaveBeenCalledTimes(1);
  });

  test('401 from loginApi (no token sent) -> handler NOT called, storage untouched, message "Invalid credentials"', async () => {
    localStorage.setItem('token', 'old');
    const handler = vi.fn();
    setUnauthorizedHandler(handler);

    mockFetch.mockResolvedValueOnce({ 
      ok: false, 
      status: 401, 
      json: async () => ({ detail: 'Invalid credentials' }) 
    });

    try {
      await loginApi({ email: 'e', password: 'p' });
      expect.fail('Should throw');
    } catch (e) {
      expect(e).toBeInstanceOf(ApiError);
      if (e instanceof ApiError) {
        expect(e.message).toBe('Invalid credentials');
      }
    }

    expect(handler).not.toHaveBeenCalled();
    expect(localStorage.getItem('token')).toBe('old');
  });

  test('422 with an array detail -> message is the first msg', async () => {
    mockFetch.mockResolvedValueOnce({ 
      ok: false, 
      status: 422, 
      json: async () => ({ detail: [{ msg: 'Field required' }] }) 
    });

    try {
      await apiFetch('/test');
      expect.fail('Should throw');
    } catch (e) {
      if (e instanceof ApiError) {
        expect(e.message).toBe('Field required');
      }
    }
  });

  test('a non-JSON error body -> message "HTTP 500"', async () => {
    mockFetch.mockResolvedValueOnce({ 
      ok: false, 
      status: 500, 
      json: async () => { throw new Error('not json'); } 
    });

    try {
      await apiFetch('/test');
      expect.fail('Should throw');
    } catch (e) {
      if (e instanceof ApiError) {
        expect(e.message).toBe('HTTP 500');
      }
    }
  });

  test('a fetch rejection -> ApiError status 0', async () => {
    mockFetch.mockRejectedValueOnce(new TypeError('Failed to fetch'));

    try {
      await apiFetch('/test');
      expect.fail('Should throw');
    } catch (e) {
      if (e instanceof ApiError) {
        expect(e.status).toBe(0);
        expect(e.message).toContain(API_BASE);
      }
    }
  });

  test('401 sent with auth true and no stored token does not call handler', async () => {
    localStorage.removeItem('token');
    const handler = vi.fn();
    setUnauthorizedHandler(handler);

    mockFetch.mockResolvedValueOnce({ 
      ok: false, 
      status: 401, 
      json: async () => ({ detail: 'Unauthorized' }) 
    });

    try {
      await apiFetch('/protected', { auth: true });
      expect.fail('Should throw');
    } catch (e) {
      if (e instanceof ApiError) {
        expect(e.status).toBe(401);
      }
    }

    expect(handler).not.toHaveBeenCalled();
  });

  test('a success returns the parsed JSON; the URL is API_BASE + path', async () => {
    mockFetch.mockResolvedValueOnce({ 
      ok: true, 
      json: async () => ({ result: 'ok' }) 
    });

    const res = await apiFetch('/success');
    expect(res).toEqual({ result: 'ok' });
    expect(mockFetch.mock.calls[0][0]).toBe(`${API_BASE}/success`);
  });
});

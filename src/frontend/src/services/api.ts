export const API_BASE: string = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

export class ApiError extends Error {
  status: number;
  detail: string;

  constructor(status: number, detail: string, message: string) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.detail = detail;
  }
}

export type UnauthorizedHandler = () => void;
let unauthorizedHandler: UnauthorizedHandler | null = null;
export const setUnauthorizedHandler = (fn: UnauthorizedHandler | null) => {
  unauthorizedHandler = fn;
};

interface ApiFetchOptions {
  method?: string;
  body?: unknown;
  auth?: boolean;
}

export async function apiFetch<T>(path: string, options: ApiFetchOptions = {}): Promise<T> {
  const { method = 'GET', body, auth = true } = options;
  const headers: Record<string, string> = {};
  
  const token = localStorage.getItem('token');
  const sentToken = auth && token !== null;
  
  if (sentToken) {
    headers['Authorization'] = `Bearer ${token}`;
  }

  if (body !== undefined) {
    headers['Content-Type'] = 'application/json';
  }

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      method,
      headers,
      body: body !== undefined ? JSON.stringify(body) : undefined,
    });
  } catch {
    throw new ApiError(0, "", `Cannot reach the API at ${API_BASE}`);
  }

  if (!response.ok) {
    if (response.status === 401 && sentToken) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      if (unauthorizedHandler) {
        unauthorizedHandler();
      }
      throw new ApiError(401, "", "Unauthorized");
    }

    let detail = "";
    let message = `HTTP ${response.status}`;
    try {
      const errData = await response.json();
      if (errData && errData.detail) {
        if (typeof errData.detail === 'string') {
          detail = errData.detail;
          message = detail;
        } else if (Array.isArray(errData.detail) && errData.detail.length > 0 && errData.detail[0].msg) {
          detail = errData.detail[0].msg;
          message = detail;
        }
      }
    } catch {
      // ignore
    }
    
    throw new ApiError(response.status, detail, message);
  }

  return response.json();
}

interface LoginResponse {
  access_token: string;
  token_type: string;
}

interface SignupResponse {
  message: string;
}

export const loginApi = (credentials: Record<string, string>) => {
  return apiFetch<LoginResponse>('/auth/login', {
    method: 'POST',
    body: credentials,
    auth: false
  });
};

export const signupApi = (data: Record<string, string>) => {
  return apiFetch<SignupResponse>('/auth/signup', {
    method: 'POST',
    body: data,
    auth: false
  });
};

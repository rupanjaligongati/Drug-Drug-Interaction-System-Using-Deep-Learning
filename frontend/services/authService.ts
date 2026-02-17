const API_BASE_URL =
  (import.meta as any).env?.VITE_API_BASE_URL || "http://localhost:8000";

interface BackendUser {
  id: number;
  name: string;
  email: string;
}

export interface AuthResult {
  access_token: string;
  user: BackendUser;
}

const handleResponse = async (res: Response): Promise<any> => {
  const data = await res.json().catch(() => ({}));

  if (!res.ok) {
    const detail =
      (data && (data.detail || data.error)) ||
      "Authentication request failed.";
    throw new Error(detail);
  }

  return data;
};

export const registerAccount = async (
  name: string,
  email: string,
  password: string
): Promise<AuthResult> => {
  const res = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ name, email, password }),
  });

  const data = await handleResponse(res);

  return {
    access_token: data.access_token,
    user: data.user,
  };
};

export const loginAccount = async (
  email: string,
  password: string
): Promise<AuthResult> => {
  const res = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await handleResponse(res);

  return {
    access_token: data.access_token,
    user: data.user,
  };
};


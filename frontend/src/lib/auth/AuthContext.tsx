import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { authApi } from "@/lib/api/endpoints";
import type { LoginResponse, UserResponse } from "@/lib/api/types";
import { clearToken, getToken, setToken } from "@/lib/auth/tokenStorage";
import {
  clearStoredUser,
  getStoredUser,
  setStoredUser,
} from "@/lib/auth/sessionUserStorage";
import { onUnauthorized } from "@/lib/auth/sessionEvents";

interface AuthContextValue {
  user: UserResponse | null;
  isAuthenticated: boolean;
  login: (username: string, password: string) => Promise<UserResponse>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function initialUser(): UserResponse | null {
  return getToken() ? getStoredUser() : null;
}

export function AuthProvider({ children }: { children: ReactNode }): ReactNode {
  const [user, setUser] = useState<UserResponse | null>(initialUser);

  const login = useCallback(
    async (username: string, password: string): Promise<UserResponse> => {
      const response: LoginResponse = await authApi.login({ username, password });
      setToken(response.token);
      setStoredUser(response.user);
      setUser(response.user);
      return response.user;
    },
    []
  );

  useEffect(() => {
    return onUnauthorized(() => {
      clearToken();
      clearStoredUser();
      setUser(null);
    });
  }, []);

  const logout = useCallback(async (): Promise<void> => {
    try {
      await authApi.logout();
    } finally {
      clearToken();
      clearStoredUser();
      setUser(null);
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, isAuthenticated: user !== null, login, logout }),
    [user, login, logout]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (context === null) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

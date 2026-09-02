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
import {
  clearStoredInstitutionName,
  getStoredInstitutionName,
  setStoredInstitutionName,
} from "@/lib/auth/sessionInstitutionStorage";
import { onUnauthorized } from "@/lib/auth/sessionEvents";

interface AuthContextValue {
  user: UserResponse | null;
  institutionName: string | null;
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
  const [institutionName, setInstitutionName] = useState<string | null>(
    getStoredInstitutionName
  );

  const login = useCallback(
    async (username: string, password: string): Promise<UserResponse> => {
      const response: LoginResponse = await authApi.login({ username, password });
      setToken(response.token);
      setStoredUser(response.user);
      setStoredInstitutionName(response.institution_name);
      setUser(response.user);
      setInstitutionName(response.institution_name);
      return response.user;
    },
    []
  );

  useEffect(() => {
    return onUnauthorized(() => {
      clearToken();
      clearStoredUser();
      clearStoredInstitutionName();
      setUser(null);
      setInstitutionName(null);
    });
  }, []);

  const logout = useCallback(async (): Promise<void> => {
    try {
      await authApi.logout();
    } finally {
      clearToken();
      clearStoredUser();
      clearStoredInstitutionName();
      setUser(null);
      setInstitutionName(null);
    }
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({ user, institutionName, isAuthenticated: user !== null, login, logout }),
    [user, institutionName, login, logout]
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

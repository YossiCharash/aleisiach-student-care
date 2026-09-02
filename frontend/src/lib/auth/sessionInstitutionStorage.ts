const INSTITUTION_KEY = "aleisiach.session.institution";

export function getStoredInstitutionName(): string | null {
  try {
    return window.localStorage.getItem(INSTITUTION_KEY);
  } catch {
    return null;
  }
}

export function setStoredInstitutionName(name: string | null): void {
  try {
    if (name === null) {
      window.localStorage.removeItem(INSTITUTION_KEY);
      return;
    }
    window.localStorage.setItem(INSTITUTION_KEY, name);
  } catch {
    // Storage unavailable; the in-memory context still holds the name for this tab.
  }
}

export function clearStoredInstitutionName(): void {
  setStoredInstitutionName(null);
}

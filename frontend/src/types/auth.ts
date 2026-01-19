export interface ApiKeys {
  anthropicKey: string;
  openaiKey: string;
}

export function hasValidKeys(keys: ApiKeys | null): boolean {
  return !!(keys?.anthropicKey && keys?.openaiKey);
}

export function saveKeys(keys: ApiKeys): void {
  sessionStorage.setItem("api_keys", JSON.stringify(keys));
}

export function loadKeys(): ApiKeys | null {
  const stored = sessionStorage.getItem("api_keys");
  if (!stored) return null;
  try {
    return JSON.parse(stored);
  } catch {
    return null;
  }
}

export function clearKeys(): void {
  sessionStorage.removeItem("api_keys");
}

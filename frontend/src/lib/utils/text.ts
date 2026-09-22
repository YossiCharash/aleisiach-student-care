export function filled(value: string | null | undefined): boolean {
  return typeof value === "string" && value.trim().length > 0;
}

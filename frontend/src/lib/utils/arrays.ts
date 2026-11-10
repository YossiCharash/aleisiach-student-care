export function toggled<T>(values: T[], value: T, on: boolean): T[] {
  return on ? [...values, value] : values.filter((item) => item !== value);
}

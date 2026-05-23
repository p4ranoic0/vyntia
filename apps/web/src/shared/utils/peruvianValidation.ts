/**
 * Peruvian identity-document and age validation helpers.
 *
 * Extracted (V4-N6) from the inline validation duplicated across the employees
 * intake flows so D-Pay and onboarding share a single source of truth instead
 * of re-implementing the rules. The rules below intentionally MIRROR the backend
 * contract (`EmpleadoCreateSerializer` in `api/v1/rrhh/serializers.py`) so the
 * frontend never accepts a value the API will reject (or vice-versa):
 *
 *   - DNI: exactly 8 numeric digits.
 *   - CE (Carné de Extranjería): 8–12 numeric digits. NOTE: the literal Bloque H
 *     brief said "9-12 alpha", but the live backend rule is 8–12 numeric. Keeping
 *     parity here is a refactor; changing the CE format is a separate product
 *     decision and would belong in a dedicated change, not this extraction.
 *   - RUC: exactly 11 numeric digits.
 *   - Minimum age 18, calendar-correct (no leap-year drift).
 */

/** True when `value` is exactly 8 numeric digits (Peruvian DNI). */
export function validateDNI(value: string): boolean {
  return /^\d{8}$/.test(value)
}

/**
 * True when `value` is 8–12 numeric digits (Carné de Extranjería).
 * Mirrors the backend rule `value.isdigit() and 8 <= len(value) <= 12`.
 */
export function validateCE(value: string): boolean {
  return /^\d{8,12}$/.test(value)
}

/** True when `value` is exactly 11 numeric digits (Peruvian RUC). */
export function validateRUC(value: string): boolean {
  return /^\d{11}$/.test(value)
}

/**
 * True when the person born on `dob` is at least 18 years old today,
 * calendar-correct (uses date arithmetic, not `days * 365`, so it does not
 * drift across leap years). A future date returns `false`.
 *
 * @param dob - birth date as a `Date` or an ISO `YYYY-MM-DD` string.
 */
export function validateAge18Plus(dob: Date | string): boolean {
  const birth = dob instanceof Date ? dob : new Date(dob)
  if (Number.isNaN(birth.getTime())) return false
  const today = new Date()
  if (birth > today) return false
  const minDob = new Date(
    today.getFullYear() - 18,
    today.getMonth(),
    today.getDate(),
  )
  // Born on or before "today minus 18 years" ⇒ already turned 18.
  return birth <= minDob
}

/**
 * Normalize a DNI for storage/display: strip non-digits and cap at 8 chars.
 * Useful as an input mask so users cannot type letters or overflow the field.
 */
export function formatDNI(value: string): string {
  return value.replace(/\D/g, '').slice(0, 8)
}

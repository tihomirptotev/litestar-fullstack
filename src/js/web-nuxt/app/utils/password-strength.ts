/**
 * Password strength & validation utilities — Nuxt port of the React app's
 * `hooks/use-validation.ts` password-related exports (constants matching the
 * backend policy: min length 12, uppercase/lowercase/digit/special required,
 * common pattern checks).
 */

const PASSWORD_MIN_LENGTH = 12
const PASSWORD_MAX_LENGTH = 128
const PASSWORD_UPPERCASE_REGEX = /[A-Z]/
const PASSWORD_LOWERCASE_REGEX = /[a-z]/
const PASSWORD_DIGIT_REGEX = /\d/
const PASSWORD_SPECIAL_REGEX = /[!@#$%^&*(),.?":{}|<>_+=\-[\]\\/~`]/
const PASSWORD_COMMON_PATTERNS = [/password/i, /123456/, /qwerty/i, /admin/i]
const PASSWORD_REPEATED_REGEX = /(.)\1{4,}/
const PASSWORD_SEQUENTIAL_REGEX = /^(012|123|234|345|456|567|678|789|890|abc|bcd|cde)/i
const PASSWORD_KEYBOARD_REGEX = /^(qwe|asd|zxc)/i

export interface PasswordStrength {
  score: number
  strength: "weak" | "medium" | "strong"
  requirements: {
    length: boolean
    uppercase: boolean
    lowercase: boolean
    digits: boolean
    special: boolean
    notCommon: boolean
  }
  feedback: string[]
}

export const validatePassword = (password: string): string | null => {
  if (!password) return null

  // Length requirements
  if (password.length < PASSWORD_MIN_LENGTH) {
    return `Password must be at least ${PASSWORD_MIN_LENGTH} characters long`
  }
  if (password.length > PASSWORD_MAX_LENGTH) {
    return `Password must not exceed ${PASSWORD_MAX_LENGTH} characters`
  }

  // Character requirements
  if (!PASSWORD_UPPERCASE_REGEX.test(password)) {
    return "Password must contain at least one uppercase letter"
  }
  if (!PASSWORD_LOWERCASE_REGEX.test(password)) {
    return "Password must contain at least one lowercase letter"
  }
  if (!PASSWORD_DIGIT_REGEX.test(password)) {
    return "Password must contain at least one digit"
  }
  if (!PASSWORD_SPECIAL_REGEX.test(password)) {
    return "Password must contain at least one special character"
  }

  // Common pattern checks
  for (const pattern of PASSWORD_COMMON_PATTERNS) {
    if (pattern.test(password)) {
      return "Password is too common - please choose a more unique password"
    }
  }

  // Repeated characters
  if (PASSWORD_REPEATED_REGEX.test(password)) {
    return "Password is too common - please choose a more unique password"
  }

  // Sequential patterns
  if (PASSWORD_SEQUENTIAL_REGEX.test(password)) {
    return "Password is too common - please choose a more unique password"
  }

  // Keyboard patterns
  if (PASSWORD_KEYBOARD_REGEX.test(password)) {
    return "Password is too common - please choose a more unique password"
  }

  return null
}

export const getPasswordStrength = (password: string): PasswordStrength => {
  const requirements = {
    length: password.length >= PASSWORD_MIN_LENGTH,
    uppercase: PASSWORD_UPPERCASE_REGEX.test(password),
    lowercase: PASSWORD_LOWERCASE_REGEX.test(password),
    digits: PASSWORD_DIGIT_REGEX.test(password),
    special: PASSWORD_SPECIAL_REGEX.test(password),
    notCommon:
      !PASSWORD_COMMON_PATTERNS.some((p) => p.test(password)) &&
      !PASSWORD_REPEATED_REGEX.test(password) &&
      !PASSWORD_SEQUENTIAL_REGEX.test(password) &&
      !PASSWORD_KEYBOARD_REGEX.test(password),
  }

  const feedback: string[] = []
  let score = 0

  // Calculate score and feedback
  if (requirements.length) {
    score += 2
  } else {
    feedback.push("Use at least 12 characters")
  }

  if (requirements.uppercase) {
    score += 1
  } else {
    feedback.push("Include uppercase letters")
  }

  if (requirements.lowercase) {
    score += 1
  } else {
    feedback.push("Include lowercase letters")
  }

  if (requirements.digits) {
    score += 1
  } else {
    feedback.push("Include numbers")
  }

  if (requirements.special) {
    score += 1
  } else {
    feedback.push("Include special characters (!@#$%^&*)")
  }

  if (requirements.notCommon) {
    score += 1
  } else {
    feedback.push("Avoid common passwords")
  }

  // Bonus points for length
  if (password.length >= 16) score += 1
  if (password.length >= 20) score += 1

  // Determine strength level
  let strength: "weak" | "medium" | "strong"
  if (score >= 7) {
    strength = "strong"
  } else if (score >= 5) {
    strength = "medium"
  } else {
    strength = "weak"
  }

  return {
    score,
    strength,
    requirements,
    feedback,
  }
}

const ALLOWED_MIME_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'text/plain',
];

const ALLOWED_EXTENSIONS = ['.pdf', '.docx', '.txt'];

const MAX_FILE_SIZE = 20 * 1024 * 1024; // 20 MB

/**
 * Validate that a file has an allowed type.
 */
export const isValidFileType = (file: File): boolean => {
  if (ALLOWED_MIME_TYPES.includes(file.type)) return true;
  const ext = '.' + file.name.split('.').pop()?.toLowerCase();
  return ALLOWED_EXTENSIONS.includes(ext);
};

/**
 * Validate that a file is within the size limit.
 */
export const isValidFileSize = (file: File): boolean => {
  return file.size <= MAX_FILE_SIZE;
};

/**
 * Get a human-readable error for file validation.
 */
export const getFileValidationError = (file: File): string | null => {
  if (!isValidFileType(file)) {
    return 'Invalid file type. Please upload a PDF, DOCX, or TXT file.';
  }
  if (!isValidFileSize(file)) {
    return 'File is too large. Maximum size is 20 MB.';
  }
  return null;
};

/**
 * Validate email format.
 */
export const isValidEmail = (email: string): boolean => {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
};

/**
 * Validate password complexity.
 * At least 8 characters, one uppercase, one lowercase, one digit.
 */
export const isValidPassword = (password: string): boolean => {
  return password.length >= 8 && /[A-Z]/.test(password) && /[a-z]/.test(password) && /\d/.test(password);
};

/**
 * Get password validation error message.
 */
export const getPasswordError = (password: string): string | null => {
  if (password.length < 8) return 'Password must be at least 8 characters.';
  if (!/[A-Z]/.test(password)) return 'Password must contain an uppercase letter.';
  if (!/[a-z]/.test(password)) return 'Password must contain a lowercase letter.';
  if (!/\d/.test(password)) return 'Password must contain a digit.';
  return null;
};

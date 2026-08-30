MIN_LENGTH = 8
MAX_LENGTH = 128


class PasswordPolicy:
    def validate(self, password: str) -> str | None:
        if len(password) < MIN_LENGTH:
            return f"הסיסמה חייבת לכלול לפחות {MIN_LENGTH} תווים."
        if len(password) > MAX_LENGTH:
            return f"הסיסמה ארוכה מדי (עד {MAX_LENGTH} תווים)."
        if not any(character.isalpha() for character in password):
            return "הסיסמה חייבת לכלול לפחות אות אחת."
        if not any(character.isdigit() for character in password):
            return "הסיסמה חייבת לכלול לפחות ספרה אחת."
        return None

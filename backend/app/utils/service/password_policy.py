class PasswordPolicy:
    def __init__(self, min_length: int, max_length: int) -> None:
        self._min_length = min_length
        self._max_length = max_length

    def validate(self, password: str) -> str | None:
        if len(password) < self._min_length:
            return f"הסיסמה חייבת לכלול לפחות {self._min_length} תווים."
        if len(password) > self._max_length:
            return f"הסיסמה ארוכה מדי (עד {self._max_length} תווים)."
        if not any(character.isalpha() for character in password):
            return "הסיסמה חייבת לכלול לפחות אות אחת."
        if not any(character.isdigit() for character in password):
            return "הסיסמה חייבת לכלול לפחות ספרה אחת."
        return None

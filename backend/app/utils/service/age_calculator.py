from datetime import date


class AgeCalculator:
    @staticmethod
    def age_in_years(date_of_birth: date, on_date: date) -> int:
        had_birthday = (on_date.month, on_date.day) >= (
            date_of_birth.month,
            date_of_birth.day,
        )
        return on_date.year - date_of_birth.year - (0 if had_birthday else 1)

def validateRequiredString(value, fieldName):
    """Memvalidasi bahwa nilai adalah string non-kosong."""
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"Field '{fieldName}' harus berupa string non-kosong.")
    return value.strip()

def validateChoice(value, choices, fieldName):
    """Memvalidasi bahwa nilai ada di dalam kumpulan pilihan (choices)."""
    if value not in choices:
        raise ValueError(f"Field '{fieldName}' harus berupa salah satu dari {choices}. Diterima: '{value}'.")
    return value

def validateInteger(value, fieldName, minValue=None):
    """Memvalidasi bahwa nilai adalah integer, opsional dengan nilai minimum."""
    if not isinstance(value, int):
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise ValueError(f"Field '{fieldName}' harus berupa bilangan bulat (integer).")
    if minValue is not None and value < minValue:
        raise ValueError(f"Field '{fieldName}' harus bernilai minimal {minValue}.")
    return value

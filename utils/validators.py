import re

class ValidationError(Exception):
    pass

def validate_phone(phone: str) -> bool:
    if not phone or not phone.strip():
        return True
    
    cleaned = (
        phone.strip()
        .replace(" ", "")
        .replace("-", "")
        .replace("(", "")
        .replace(")", "")
    )

    if not cleaned.isdigit():
        raise ValidationError("Phone number must contain only digits")

    if len(cleaned) != 10:
        raise ValidationError("Phone number must be exactly 10 digits long")

def validate_quantity(quantity: int) -> bool:
    if quantity < 0:
        raise ValidationError("Quantity cannot be negative")
    return True
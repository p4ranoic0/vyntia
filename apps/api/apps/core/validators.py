"""Reusable validators for API endpoints."""

import re
from typing import Any, List, Optional
from datetime import date, datetime
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


class RUTValidator:
    """Validator for Chilean RUT (Role Único Tributario)."""
    
    def __init__(self, message: Optional[str] = None):
        self.message = message or "RUT inválido"
    
    def __call__(self, value: str) -> None:
        """Validate RUT format and check digit.
        
        Args:
            value: RUT string to validate
            
        Raises:
            ValidationError: If RUT is invalid
        """
        if not value:
            raise ValidationError(self.message)
            
        # Remove dots and hyphens
        rut = re.sub(r'[.-]', '', str(value).upper())
        
        # Check format
        if not re.match(r'^\d{7,8}[0-9K]$', rut):
            raise ValidationError(self.message)
            
        # Extract number and check digit
        rut_number = rut[:-1]
        check_digit = rut[-1]
        
        # Calculate check digit
        calculated_digit = self._calculate_check_digit(rut_number)
        
        if check_digit != calculated_digit:
            raise ValidationError(self.message)
    
    def _calculate_check_digit(self, rut_number: str) -> str:
        """Calculate RUT check digit.
        
        Args:
            rut_number: RUT number without check digit
            
        Returns:
            str: Calculated check digit
        """
        multipliers = [2, 3, 4, 5, 6, 7]
        total = 0
        
        for i, digit in enumerate(reversed(rut_number)):
            multiplier = multipliers[i % len(multipliers)]
            total += int(digit) * multiplier
            
        remainder = total % 11
        check_digit = 11 - remainder
        
        if check_digit == 11:
            return '0'
        elif check_digit == 10:
            return 'K'
        else:
            return str(check_digit)


class PhoneValidator(RegexValidator):
    """Validator for Chilean phone numbers."""
    
    regex = r'^(\+56)?[2-9]\d{8}$'
    message = 'Número de teléfono inválido. Formato: +56912345678 o 912345678'


class EmailDomainValidator:
    """Validator for specific email domains."""
    
    def __init__(self, allowed_domains: List[str], message: Optional[str] = None):
        self.allowed_domains = [domain.lower() for domain in allowed_domains]
        self.message = message or f"Email debe ser de uno de estos dominios: {', '.join(allowed_domains)}"
    
    def __call__(self, value: str) -> None:
        """Validate email domain.
        
        Args:
            value: Email to validate
            
        Raises:
            ValidationError: If domain is not allowed
        """
        if not value:
            return
            
        domain = value.split('@')[-1].lower()
        if domain not in self.allowed_domains:
            raise ValidationError(self.message)


class DateRangeValidator:
    """Validator for date ranges."""
    
    def __init__(
        self,
        min_date: Optional[date] = None,
        max_date: Optional[date] = None,
        message: Optional[str] = None
    ):
        self.min_date = min_date
        self.max_date = max_date
        self.message = message or "Fecha fuera del rango permitido"
    
    def __call__(self, value: date) -> None:
        """Validate date is within range.
        
        Args:
            value: Date to validate
            
        Raises:
            ValidationError: If date is out of range
        """
        if not value:
            return
            
        if self.min_date and value < self.min_date:
            raise ValidationError(f"Fecha no puede ser anterior a {self.min_date}")
            
        if self.max_date and value > self.max_date:
            raise ValidationError(f"Fecha no puede ser posterior a {self.max_date}")


class AgeValidator:
    """Validator for age based on birth date."""
    
    def __init__(self, min_age: int = 18, max_age: int = 100, message: Optional[str] = None):
        self.min_age = min_age
        self.max_age = max_age
        self.message = message or f"Edad debe estar entre {min_age} y {max_age} años"
    
    def __call__(self, value: date) -> None:
        """Validate age based on birth date.
        
        Args:
            value: Birth date
            
        Raises:
            ValidationError: If age is out of range
        """
        if not value:
            return
            
        today = date.today()
        age = today.year - value.year - ((today.month, today.day) < (value.month, value.day))
        
        if age < self.min_age or age > self.max_age:
            raise ValidationError(self.message)


class SalaryValidator:
    """Validator for salary amounts."""
    
    def __init__(
        self,
        min_salary: int = 350000,  # Chilean minimum wage
        max_salary: int = 50000000,
        message: Optional[str] = None
    ):
        self.min_salary = min_salary
        self.max_salary = max_salary
        self.message = message or f"Salario debe estar entre ${min_salary:,} y ${max_salary:,}"
    
    def __call__(self, value: int) -> None:
        """Validate salary amount.
        
        Args:
            value: Salary amount
            
        Raises:
            ValidationError: If salary is out of range
        """
        if not value:
            return
            
        if value < self.min_salary or value > self.max_salary:
            raise ValidationError(self.message)


class FileExtensionValidator:
    """Validator for file extensions."""
    
    def __init__(self, allowed_extensions: List[str], message: Optional[str] = None):
        self.allowed_extensions = [ext.lower() for ext in allowed_extensions]
        self.message = message or f"Extensiones permitidas: {', '.join(allowed_extensions)}"
    
    def __call__(self, value) -> None:
        """Validate file extension.
        
        Args:
            value: File object or filename
            
        Raises:
            ValidationError: If extension is not allowed
        """
        if not value:
            return
            
        filename = getattr(value, 'name', str(value))
        extension = filename.split('.')[-1].lower() if '.' in filename else ''
        
        if extension not in self.allowed_extensions:
            raise ValidationError(self.message)


class FileSizeValidator:
    """Validator for file size."""
    
    def __init__(self, max_size_mb: int = 5, message: Optional[str] = None):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.message = message or f"Archivo no puede exceder {max_size_mb}MB"
    
    def __call__(self, value) -> None:
        """Validate file size.
        
        Args:
            value: File object
            
        Raises:
            ValidationError: If file is too large
        """
        if not value:
            return
            
        if hasattr(value, 'size') and value.size > self.max_size_bytes:
            raise ValidationError(self.message)


class PasswordStrengthValidator:
    """Validator for password strength."""
    
    def __init__(
        self,
        min_length: int = 8,
        require_uppercase: bool = True,
        require_lowercase: bool = True,
        require_numbers: bool = True,
        require_special: bool = True,
        message: Optional[str] = None
    ):
        self.min_length = min_length
        self.require_uppercase = require_uppercase
        self.require_lowercase = require_lowercase
        self.require_numbers = require_numbers
        self.require_special = require_special
        self.message = message or "Contraseña no cumple con los requisitos de seguridad"
    
    def __call__(self, value: str) -> None:
        """Validate password strength.
        
        Args:
            value: Password to validate
            
        Raises:
            ValidationError: If password is weak
        """
        if not value:
            return
            
        errors = []
        
        if len(value) < self.min_length:
            errors.append(f"Debe tener al menos {self.min_length} caracteres")
            
        if self.require_uppercase and not re.search(r'[A-Z]', value):
            errors.append("Debe contener al menos una letra mayúscula")
            
        if self.require_lowercase and not re.search(r'[a-z]', value):
            errors.append("Debe contener al menos una letra minúscula")
            
        if self.require_numbers and not re.search(r'\d', value):
            errors.append("Debe contener al menos un número")
            
        if self.require_special and not re.search(r'[!@#$%^&*(),.?":{}|<>]', value):
            errors.append("Debe contener al menos un carácter especial")
            
        if errors:
            raise ValidationError(f"{self.message}: {'; '.join(errors)}")


class UniqueFieldValidator:
    """Validator for unique fields across models."""
    
    def __init__(self, model_class, field_name: str, exclude_pk: Optional[int] = None, message: Optional[str] = None):
        self.model_class = model_class
        self.field_name = field_name
        self.exclude_pk = exclude_pk
        self.message = message or f"{field_name} ya existe"
    
    def __call__(self, value: Any) -> None:
        """Validate field uniqueness.
        
        Args:
            value: Field value to validate
            
        Raises:
            ValidationError: If value is not unique
        """
        if not value:
            return
            
        queryset = self.model_class.objects.filter(**{self.field_name: value})
        
        if self.exclude_pk:
            queryset = queryset.exclude(pk=self.exclude_pk)
            
        if queryset.exists():
            raise ValidationError(self.message)


class ConditionalValidator:
    """Validator that applies based on a condition."""
    
    def __init__(self, condition_func, validator, message: Optional[str] = None):
        self.condition_func = condition_func
        self.validator = validator
        self.message = message
    
    def __call__(self, value: Any) -> None:
        """Apply validator if condition is met.
        
        Args:
            value: Value to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if self.condition_func(value):
            try:
                self.validator(value)
            except ValidationError as e:
                if self.message:
                    raise ValidationError(self.message)
                raise e


# Common validator instances
rut_validator = RUTValidator()
phone_validator = PhoneValidator()
chilean_phone_validator = PhoneValidator()
company_email_validator = EmailDomainValidator(['empresa.cl', 'company.com'])
employee_age_validator = AgeValidator(min_age=18, max_age=65)
chilean_salary_validator = SalaryValidator()
image_file_validator = FileExtensionValidator(['jpg', 'jpeg', 'png', 'gif'])
document_file_validator = FileExtensionValidator(['pdf', 'doc', 'docx'])
small_file_validator = FileSizeValidator(max_size_mb=2)
strong_password_validator = PasswordStrengthValidator()
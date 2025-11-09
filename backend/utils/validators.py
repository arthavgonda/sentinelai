import re
import email.utils
from typing import Tuple, Optional, List

def validate_email(email_str: str) -> Tuple[bool, Optional[str]]:
    try:
        email.utils.parseaddr(email_str)
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if re.match(pattern, email_str):
            return True, None
        return False, "Invalid email format"
    except:
        return False, "Invalid email format"

def validate_phone(phone: str) -> Tuple[bool, Optional[str]]:
    cleaned = re.sub(r'[^\d+]', '', phone)
    if len(cleaned) < 10 or len(cleaned) > 15:
        return False, "Invalid phone number length"
    pattern = r'^\+?[1-9]\d{1,14}$'
    if re.match(pattern, cleaned):
        return True, None
    return False, "Invalid phone number format"

def validate_username(username: str) -> Tuple[bool, Optional[str]]:
    if len(username) < 3 or len(username) > 30:
        return False, "Username must be between 3 and 30 characters"
    pattern = r'^[a-zA-Z0-9._-]+$'
    if re.match(pattern, username):
        return True, None
    return False, "Username contains invalid characters"

def validate_name(name: str) -> Tuple[bool, Optional[str]]:
    name = name.strip()
    if len(name) < 2:
        return False, "Name must be at least 2 characters"
    if len(name) > 100:
        return False, "Name must be less than 100 characters"
    pattern = r'^[a-zA-Z\s\-\'\.]+$'
    if re.match(pattern, name):
        return True, None
    return False, "Name contains invalid characters"

def normalize_email(email_str: str) -> str:
    email_str = email_str.lower().strip()
    if '+' in email_str:
        local, domain = email_str.split('@', 1)
        local = local.split('+')[0]
        email_str = f"{local}@{domain}"
    return email_str

def normalize_phone(phone: str) -> str:
    cleaned = re.sub(r'[^\d+]', '', phone)
    if not cleaned.startswith('+'):
        if cleaned.startswith('1') and len(cleaned) == 11:
            cleaned = '+' + cleaned
        elif len(cleaned) == 10:
            cleaned = '+1' + cleaned
        else:
            cleaned = '+' + cleaned
    return cleaned

def normalize_username(username: str) -> str:
    return username.lower().strip()

def extract_domain(email_str: str) -> str:
    try:
        return email_str.split('@')[1].lower()
    except:
        return ""

def generate_username_variations(username: str) -> List[str]:
    variations = [username.lower(), username.lower().replace('_', ''), username.lower().replace('.', '')]
    if '.' in username:
        parts = username.split('.')
        variations.append(''.join(parts))
        variations.append(parts[0])
        variations.append(parts[-1])
    return list(set(variations))

def sanitize_input(input_str: str) -> str:
    return re.sub(r'[<>"\';]', '', input_str.strip())

def normalize_name(name: str) -> str:
    return " ".join(name.strip().split())

def generate_name_variations(name: str) -> List[str]:
    name = normalize_name(name)
    variations = [name, name.lower(), name.title(), name.upper()]
    
    parts = name.split()
    if len(parts) > 1:
        variations.append(parts[0])
        variations.append(parts[-1])
        variations.append(f"{parts[0]} {parts[-1]}")
        variations.append(f"{parts[0][0]}. {parts[-1]}" if len(parts[0]) > 0 else parts[-1])
        variations.append(f"{parts[0]} {parts[-1][0]}." if len(parts[-1]) > 0 else parts[0])
    
    return list(set([v for v in variations if v]))


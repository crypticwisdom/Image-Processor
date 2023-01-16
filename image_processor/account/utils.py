import re
from .models import ApplicationExtension, ApplicationContentType

# Query list of Available extension-id
list_of_extensions = [extension.id for extension in ApplicationExtension.objects.all()]

# Query list of Available content type-id
list_of_content_types = [content_type.id for content_type in ApplicationContentType.objects.all()]


def validate_email(email):
    try:
        regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        if re.fullmatch(regex, email):
            return True
        return False
    except (TypeError, Exception) as err:
        # Log error
        return False


def validate_text(text):
    try:
        if text:
            for i in text:
                if i in ('!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '+', '=', '[', ']', '{', '}', '|', '\\',
                         ',', '.', '<', '>', '?', '/', '"', "'", '`', '~'):
                    return False
        return True
    except (Exception,) as err:
        return False


def validate_password(password):
    try:
        reg = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,20}$"

        # compiling regex
        pat = re.compile(reg)

        # searching regex
        mat = re.search(pat, password)

        # validating conditions
        if mat:
            return True, "Valid."
        return False, "Invalid, Password length must be greater than 6 and must consist of a Capitalized letter, " \
                      "special character and a digit."
    except (Exception,) as err:
        return False, "{error}".format(error=err)


def convert_to_kb(unit, value):
    """
        Parameters Description:
            unit: receives 'kb' or 'mb'. The unit of the file size.
            value: value of the file size

        Rates in use:
        1024 KB -> 1MB
        Example: 9MB to KB = 9 * 1024 = 9216KB
    """
    try:
        unit, value = str(unit), str(value)

        if not value.isnumeric():
            return False, "Expects numbers only"

        if unit.lower() not in ['b', 'kb', 'mb']:
            return False, "Expects 'kb' or 'mb' only"

        SIZE_CONSTANT: float = 1000  # By computer science it is 1024

        value = float(value)
        if unit == "kb":
            return True, value
        elif unit == "mb":
            return True, SIZE_CONSTANT * float(value)
        elif unit == "b":
            # convert Bytes to KiloBytes
            return True, value / SIZE_CONSTANT
    except (Exception,) as err:
        return False, err

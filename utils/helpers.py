import re

# Helpers de formatação
def format_cpf(cpf):
    if not cpf:
        return ''
    s = re.sub(r"\D", "", str(cpf))
    if len(s) == 11:
        return f"{s[:3]}.{s[3:6]}.{s[6:9]}-{s[9:]}"
    return str(cpf)


def format_isbn(isbn):
    if not isbn:
        return ''
    s = re.sub(r"\D", "", str(isbn))
    # ISBN-13 -> group 3-1-2-6-1 (approx)
    if len(s) == 13:
        return f"{s[:3]}-{s[3]}-{s[4:6]}-{s[6:12]}-{s[12]}"
    # ISBN-10 -> group 1-3-5-1 (approx)
    if len(s) == 10:
        return f"{s[:1]}-{s[1:4]}-{s[4:9]}-{s[9]}"
    return str(isbn)
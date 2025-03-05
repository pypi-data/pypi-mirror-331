def remove_quote(s: str) -> str:
    if len(s) <= 2:
        return s
    if s[0] == "'" and s[-1] == "'":
        return s[1:-1]
    if s[0] == '"' and s[-1] == '"':
        return s[1:-1]
    return s

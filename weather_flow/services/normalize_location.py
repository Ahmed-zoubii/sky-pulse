import re


def normalize_location(location: str):
    """
    Clean up a user‐supplied location string so that downstream services
    always receive a predictable “Title Case” name without stray junk.
    """
    loc = location.strip()
    # 2. Collapse whitespace
    loc = re.sub(r'\s+', ' ', loc)
    # 3. Remove unwanted chars
    loc = re.sub(r"[^A-Za-z\s,'-]", '', loc)
    # 4. Split on commas, trim
    parts = [part.strip() for part in loc.split(',') if part.strip()]

    def title_word(word: str) -> str:
        # this regex matches sequences of letters possibly joined by ' or -
        return re.sub(
            r"[A-Za-z]+(?:['-][A-Za-z]+)*",
            lambda m: m.group(0).capitalize(),
            word
        )

    # 5. Title-case each part word-by-word
    titled_parts = []
    for part in parts:
        words = part.split(' ')
        titled_parts.append(' '.join(title_word(w) for w in words))

    # 6. Rejoin
    normalized = ', '.join(titled_parts)

    # 7. Special cases
    special_cases = {
        'uk': 'UK',
        'usa': 'USA',
        'ksa': 'Saudi Arabia'
    }
    lower = normalized.lower()
    if lower in special_cases:
        return special_cases[lower]

    return normalized

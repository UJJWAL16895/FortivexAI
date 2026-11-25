"""Recognize a small, explicit set of lead details without guessing at STT errors."""

import calendar
import re
from datetime import date, timedelta

EN_NUMBERS = dict(
    zip("one two three four five six seven eight nine ten".split(), range(1, 11), strict=True)
)
HI_NUMBERS = dict(zip("एक दो तीन चार पाँच छह सात आठ नौ दस".split(), range(1, 11), strict=True))
ROMAN_NUMBERS = dict(
    zip("ek do teen chaar paanch chhe saat aath nau das".split(), range(1, 11), strict=True)
)
NUMBERS = EN_NUMBERS | HI_NUMBERS | ROMAN_NUMBERS | {"पांच": 5, "char": 4, "panch": 5}
STORE_COUNT = re.compile(
    r"(?<!\w)(\d{1,4}|"
    + "|".join(NUMBERS)
    + r")\s+(?:stores?\b|locations?\b|dukaan(?:en)?\b|दुकानें|दुकानों|दुकान)",
    re.I,
)
MISHEARD_STORES = re.compile(r"\bfree\s+(?:stores?|locations?)\b|फ्री\s+दुकान", re.I)
ISO_DATE = re.compile(r"\b\d{4}-\d{2}-\d{2}\b")
MONTHS = {name.casefold(): i for i, name in enumerate(calendar.month_name) if i}
MONTHS.update(
    zip(
        "जनवरी फ़रवरी मार्च अप्रैल मई जून जुलाई अगस्त सितंबर अक्टूबर नवंबर दिसंबर".split(),
        range(1, 13),
        strict=True,
    )
)
MONTHS.update({"फरवरी": 2, "सितम्बर": 9, "नवम्बर": 11, "दिसम्बर": 12})
MONTH_DATE = re.compile(r"\b(\d{1,2})\s+(" + "|".join(MONTHS) + r")(?:\s+(\d{4}))?\b", re.I)
WEEKDAYS = {name.casefold(): i for i, name in enumerate(calendar.day_name)}
WEEKDAYS.update(
    zip("सोमवार मंगलवार बुधवार गुरुवार शुक्रवार शनिवार रविवार".split(), range(7), strict=True)
)
WEEKDAY = re.compile(r"(?<!\w)(" + "|".join(WEEKDAYS) + r")(?!\w)", re.I)


def store_count(text: str) -> int | None:
    match = STORE_COUNT.search(text)
    if match is None:
        return None
    term = match[1].casefold()
    value = int(term) if term.isdecimal() else NUMBERS[term]
    return value or None


def target_date(text: str, today: date) -> date | None:
    try:
        if match := ISO_DATE.search(text):
            return date(*(int(part) for part in match[0].split("-")))
        if match := MONTH_DATE.search(text):
            month = MONTHS[match[2].casefold()]
            day = int(match[1])
            year = (
                int(match[3])
                if match[3]
                else today.year + ((month, day) < (today.month, today.day))
            )
            return date(year, month, day)
        if re.search(r"\btomorrow\b", text, re.I):
            return today + timedelta(days=1)
        if match := WEEKDAY.search(text):
            return today + timedelta(days=(WEEKDAYS[match[1].casefold()] - today.weekday()) % 7)
    except (ValueError, OverflowError):
        return None
    return None

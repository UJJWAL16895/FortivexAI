"""Shared language hint and copy for unsupported product facts."""

import re

PRODUCT_QUESTION = re.compile(
    r"\b(price|pricing|cost|discount|offer|quote|rupees?|features?|integrations?|supports?)\b"
    r"|कीमत|छूट|दाम|सुविधा",
    re.I,
)
HINDI = re.compile(r"[\u0900-\u097f]")
CHECK_SHORT_EN = "I’ll check with our team and can offer a human follow-up."
CHECK_SHORT_HI = "मैं टीम से पूछकर किसी व्यक्ति से बात कराने की पेशकश कर सकता हूँ।"

"""Until retrieval exists, only reviewed sentences can leave the backend."""

import re

PRODUCT_QUESTION = re.compile(
    r"\b(price|pricing|cost|discount|offer|quote|rupees?|features?|integrations?|supports?)\b"
    r"|कीमत|छूट|दाम|सुविधा",
    re.I,
)
HINDI = re.compile(r"[\u0900-\u097f]")
CHECK_EN = ("I’ll check that with our team.", "Would you like a human follow-up?")
CHECK_HI = ("मैं टीम से इसकी जानकारी लूँगा।", "क्या आप हमारी टीम से बात करना चाहेंगे?")
CHECK_SHORT_EN = "I’ll check with our team and can offer a human follow-up."
CHECK_SHORT_HI = "मैं टीम से पूछकर किसी व्यक्ति से बात कराने की पेशकश कर सकता हूँ।"
APPROVED = {
    *CHECK_EN,
    *CHECK_HI,
    "How many locations do you manage today?",
    "What would you like to see in a demo?",
    "What would you like to improve about how you track inventory today?",
    "आप कितनी दुकानें संभालते हैं?",
    "आप डेमो में क्या देखना चाहेंगे?",
}


def follow_up(text: str) -> tuple[str, str]:
    return CHECK_HI if HINDI.search(text) else CHECK_EN

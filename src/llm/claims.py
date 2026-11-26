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


SMALL_TALK = {
    "hello": "Nice to meet you! Are you managing one store or several?",
    "well": "Doing well, thanks! Are you managing one store or several?",
    "thanks": "You’re welcome! What would you like to improve about your inventory?",
    "ok": "Sounds good! What would you like to know about tracking stock?",
}
SMALL_TALK_HI = {
    "hello": "नमस्ते! आप एक दुकान संभालते हैं या कई?",
    "well": "मैं ठीक हूँ, धन्यवाद! आप एक दुकान संभालते हैं या कई?",
    "thanks": "आपका स्वागत है! स्टॉक संभालने में आपको किस चीज़ की मदद चाहिए?",
    "ok": "ठीक है! स्टॉक के बारे में आप क्या जानना चाहेंगे?",
}
PLEASANTRIES = {
    "hello": {"hello", "hi", "hey", "hello there", "namaste", "namaskar", "नमस्ते", "नमस्कार", "हैलो"},
    "well": {"how are you", "kaise ho", "kaise hain", "aap kaise hain", "कैसे हो", "आप कैसे हैं", "कैसे हैं"},
    "thanks": {
        "thanks",
        "thank you",
        "thanks a lot",
        "shukriya",
        "dhanyavaad",
        "dhanyavad",
        "शुक्रिया",
        "धन्यवाद",
    },
    "ok": {"ok", "okay", "ok thanks", "theek hai", "thik hai", "achha", "ठीक है", "अच्छा", "ओके"},
}


def small_talk(text: str) -> str | None:
    token = " ".join(text.casefold().strip(" .!?,।").split())
    for kind, variants in PLEASANTRIES.items():
        if token in variants:
            return (SMALL_TALK_HI if HINDI.search(text) else SMALL_TALK)[kind]
    return None

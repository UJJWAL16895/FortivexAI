import logging
import re

EMAIL = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")
PHONE = re.compile(r"(?<!\w)\+?\d(?:[ ()-]*\d){9,14}(?!\d)")


class RedactContacts(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.msg = PHONE.sub("[phone]", EMAIL.sub("[email]", record.getMessage()))
        record.args = ()
        if record.exc_info:
            record.msg += " [" + record.exc_info[0].__name__ + "]" if record.exc_info[0] else ""
            record.exc_info = None
            record.exc_text = None
        return True


def protect_server_logs() -> None:
    for name in ("uvicorn", "uvicorn.error", "uvicorn.access", "httpx"):
        logger = logging.getLogger(name)
        if not any(isinstance(item, RedactContacts) for item in logger.filters):
            logger.addFilter(RedactContacts())

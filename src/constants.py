import re
from enum import Enum

BASIC_NOTE_TYPE_NAME = "Basic"
DUPLICARD_TYPE_NAME = "X-DupliCard"

SEPARATOR = "<br />"
SEPARATOR_REGEX = re.compile(r"<br ?/?>")  # Anki may remove / from <br />

NOTE_TYPE_NAME_FIELD = "name"
NOTE_TYPE_FIELDS_FIELD = "flds"
NOTE_TYPE_FIELDS_NAME_FIELD = "name"
NOTE_TYPE_FIELDS_ORDER_FIELD = "ord"
NOTE_TYPE_FIELDS_TYPE_NAME = "Type"
NOTE_TYPE_FIELDS_TO_IGNORE = ("id", NOTE_TYPE_NAME_FIELD)

SORTER_CONFIG_KEY = "sorter"
SORTER_FUNCTION_NAME = "sorter"
SORTER_FUNCTION_BODY_TEMPLATE = "def sorter(entry):\n{}"


class DuplicardTypeField(Enum):
    FrontToBack = "FB"
    BackToFront = "BF"


class ErrorMessages:
    DID_NOT_FIND_NOTE_TYPE = f"Did not find {BASIC_NOTE_TYPE_NAME} note type."
    NO_MW = "mw is none."

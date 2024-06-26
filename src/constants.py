BASIC_NOTE_TYPE_NAME = "Basic"
DUPLICARD_TYPE_NAME = "X-DupliCard"

SEPARATOR = "<br />"

NOTE_TYPE_NAME_FIELD = "name"
NOTE_TYPE_FIELDS_TO_IGNORE = ("id", NOTE_TYPE_NAME_FIELD)


class ErrorMessages:
    DID_NOT_FIND_NOTE_TYPE = f"Did not find {BASIC_NOTE_TYPE_NAME} note type."
    NO_MW = "mw is none."

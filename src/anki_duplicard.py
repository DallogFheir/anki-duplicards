import anki.consts
import anki.hooks as hooks
from anki.cards import Card
from anki.collection import Collection
from anki.decks import DeckId
from anki.notes import Note, NoteId
from aqt import gui_hooks, mw

from .constants import (
    BASIC_NOTE_TYPE_NAME,
    DUPLICARD_TYPE_NAME,
    NOTE_TYPE_FIELDS_TO_IGNORE,
    NOTE_TYPE_NAME_FIELD,
    SEPARATOR,
    ErrorMessages,
)


class AnkiDuplicard:
    def __init__(self) -> None:
        if mw is None:
            raise RuntimeError(ErrorMessages.NO_MW)

        self._mw = mw
        self._currently_adding = False

    def run(self) -> None:
        if not self._try_add_custom_note_type():
            gui_hooks.collection_did_load.append(self._add_custom_note_type)

        hooks.note_will_be_added.append(self._handle_note_add)

    def _add_custom_note_type(self, *_) -> None:
        self._try_add_custom_note_type()

    def _try_add_custom_note_type(self) -> bool:
        collection = self._mw.col

        if collection is None:
            return False

        models = collection.models

        if models.by_name(DUPLICARD_TYPE_NAME) is not None:
            return False

        basic_card = models.by_name(BASIC_NOTE_TYPE_NAME)

        if basic_card is None:
            raise RuntimeError(ErrorMessages.DID_NOT_FIND_NOTE_TYPE)

        duplicard_note_type = models.new(DUPLICARD_TYPE_NAME)
        duplicard_note_type[NOTE_TYPE_NAME_FIELD] = DUPLICARD_TYPE_NAME

        for field_name, field in basic_card.items():
            if field_name not in NOTE_TYPE_FIELDS_TO_IGNORE:
                duplicard_note_type[field_name] = field

        models.add_dict(duplicard_note_type)
        return True

    def _make_search_string(self, text: str) -> str:
        return f'"front:{text}" "note:{DUPLICARD_TYPE_NAME}"'

    def _add_simple_card(
        self,
        collection: Collection,
        deck_id: DeckId,
        question: str,
        answer: str,
        tags: list[str],
    ) -> None:
        models = collection.models
        duplicard_note_type = models.by_name(DUPLICARD_TYPE_NAME)

        if duplicard_note_type is None:
            raise RuntimeError(ErrorMessages.DID_NOT_FIND_NOTE_TYPE)

        note = collection.new_note(duplicard_note_type)
        note.fields = [question, answer]
        note.tags = tags

        self._currently_adding = True
        collection.add_note(note, deck_id)
        self._currently_adding = False

    def _forget_card(self, collection: Collection, card: Card) -> None:
        card.type = anki.consts.CARD_TYPE_NEW
        card.queue = anki.consts.QUEUE_TYPE_NEW
        card.left = 0
        card.ivl = 0
        card.due = 0
        card.odue = 0

        collection.update_card(card)

    def _update_existing_cards(
        self,
        collection: Collection,
        ids: list[NoteId],
        question: str,
        answer: str,
        tags: list[str],
    ) -> None:
        for id in ids:
            other_note = collection.get_note(id)
            other_question = other_note.fields[0]

            answer_to_add = answer if question == other_question else question

            other_note.fields[1] += f"{SEPARATOR}{answer_to_add}"
            other_note.tags += tags

            card = other_note.cards()[0]
            self._forget_card(collection, card)

            collection.update_note(other_note)

    def _handle_note_add(
        self, collection: Collection, note: Note, deck_id: DeckId
    ) -> None:
        if self._currently_adding:
            return

        collection._prevent_add_note = False  # type: ignore

        note_type = note.note_type()

        if note_type is None or note_type[NOTE_TYPE_NAME_FIELD] != DUPLICARD_TYPE_NAME:
            return

        question, answer = note.fields
        tags = note.tags

        same_questions = collection.find_notes(self._make_search_string(question))
        same_answers = collection.find_notes(self._make_search_string(answer))

        same_ids = [
            *collection.find_notes(self._make_search_string(question)),
            *collection.find_notes(self._make_search_string(answer)),
        ]
        self._update_existing_cards(collection, same_ids, question, answer, tags)

        if not same_questions:
            self._add_simple_card(collection, deck_id, question, answer, tags)
        if not same_answers:
            self._add_simple_card(collection, deck_id, answer, question, tags)

        collection._prevent_add_note = True  # type: ignore

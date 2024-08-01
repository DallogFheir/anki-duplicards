import re

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
    NOTE_TYPE_FIELDS_FIELD,
    NOTE_TYPE_FIELDS_NAME_FIELD,
    NOTE_TYPE_FIELDS_ORDER_FIELD,
    NOTE_TYPE_FIELDS_TO_IGNORE,
    NOTE_TYPE_FIELDS_TYPE_NAME,
    NOTE_TYPE_NAME_FIELD,
    SEPARATOR,
    SEPARATOR_REGEX,
    SORTER_CONFIG_KEY,
    SORTER_FUNCTION_BODY_TEMPLATE,
    SORTER_FUNCTION_NAME,
    DuplicardTypeField,
    ErrorMessages,
)


class AnkiDuplicards:
    def __init__(self) -> None:
        if mw is None:
            raise RuntimeError(ErrorMessages.NO_MW)

        self._mw = mw

        config = mw.addonManager.getConfig(__name__)
        self.sorter = self._parse_sorter(config[SORTER_CONFIG_KEY])

        self._currently_adding = False

    def run(self) -> None:
        if not self._try_add_custom_note_type():
            gui_hooks.collection_did_load.append(self._add_custom_note_type)

        hooks.note_will_be_added.append(self._handle_note_add)

    def _parse_sorter(self, sorter_code: str) -> None:
        sorter_code_lines = sorter_code.split("\n")
        sorter_code_with_indent = "\n".join(f"    {line}" for line in sorter_code_lines)

        sorter_function_body = SORTER_FUNCTION_BODY_TEMPLATE.format(
            sorter_code_with_indent
        )

        local_vars = {}

        exec(sorter_function_body, {}, local_vars)

        self._sorter = local_vars[SORTER_FUNCTION_NAME]

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
                if field_name == NOTE_TYPE_FIELDS_FIELD:
                    max_order = max(f[NOTE_TYPE_FIELDS_ORDER_FIELD] for f in field)
                    new_order = max_order + 1

                    field_template = {**field[-1]}
                    field_template[NOTE_TYPE_FIELDS_NAME_FIELD] = (
                        NOTE_TYPE_FIELDS_TYPE_NAME
                    )
                    field_template[NOTE_TYPE_FIELDS_ORDER_FIELD] = new_order

                    field.append(field_template)

                duplicard_note_type[field_name] = field

        models.add_dict(duplicard_note_type)
        return True

    def _make_search_string(self, text: str, deck_name: str) -> str:
        return f'"front:{text}" "note:{DUPLICARD_TYPE_NAME}" "deck:{deck_name}"'

    def _add_simple_card(
        self,
        collection: Collection,
        deck_id: DeckId,
        question: str,
        answer: str,
        type: DuplicardTypeField,
        tags: list[str],
    ) -> None:
        models = collection.models
        duplicard_note_type = models.by_name(DUPLICARD_TYPE_NAME)

        if duplicard_note_type is None:
            raise RuntimeError(ErrorMessages.DID_NOT_FIND_NOTE_TYPE)

        note = collection.new_note(duplicard_note_type)
        note.fields = [question, answer, type.value]
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

            current_answers = re.split(SEPARATOR_REGEX, other_note.fields[1])
            current_answers.append(answer_to_add)
            current_answers.sort(key=self._sorter)

            other_note.fields[1] = SEPARATOR.join(current_answers)
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

        deck = collection.decks.get(deck_id)
        if deck is None:
            return
        deck_name = deck["name"]

        note_type = note.note_type()

        if note_type is None or note_type[NOTE_TYPE_NAME_FIELD] != DUPLICARD_TYPE_NAME:
            return

        question, answer, _ = note.fields
        tags = note.tags

        same_questions = collection.find_notes(
            self._make_search_string(question, deck_name)
        )
        same_answers = collection.find_notes(
            self._make_search_string(answer, deck_name)
        )

        same_ids = [
            *collection.find_notes(self._make_search_string(question, deck_name)),
            *collection.find_notes(self._make_search_string(answer, deck_name)),
        ]
        self._update_existing_cards(collection, same_ids, question, answer, tags)

        if not same_questions:
            self._add_simple_card(
                collection,
                deck_id,
                question,
                answer,
                DuplicardTypeField.FrontToBack,
                tags,
            )
        if not same_answers:
            self._add_simple_card(
                collection,
                deck_id,
                answer,
                question,
                DuplicardTypeField.BackToFront,
                tags,
            )

        collection._prevent_add_note = True  # type: ignore

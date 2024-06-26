from typing import Any, Union

import anki.hooks as hooks
from anki import collection_pb2
from anki.collection import Collection
from anki.decks import DeckId
from anki.notes import Note, NoteId

from .src.anki_duplicard import AnkiDuplicard


# begin 🙈
class DummyChanges:
    def __getattribute__(self, name: str) -> Union[list[Any], "DummyChanges"]:
        if name == "fields":
            return []

        return self


def add_note_MONKEY_PATCH(
    self: Collection, note: Note, deck_id: DeckId
) -> Union[DummyChanges, collection_pb2.OpChanges]:
    hooks.note_will_be_added(self, note, deck_id)

    if self._prevent_add_note:  # type: ignore
        return DummyChanges()

    out = self._backend.add_note(note=note._to_backend_note(), deck_id=deck_id)
    note.id = NoteId(out.note_id)
    return out.changes


Collection.add_note = add_note_MONKEY_PATCH  # type: ignore
# end 🙈


AnkiDuplicard().run()

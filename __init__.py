import anki.hooks as hooks
from anki import collection_pb2
from anki.collection import Collection
from anki.decks import DeckId
from anki.notes import Note, NoteId

from .src.anki_duplicard import AnkiDuplicard


# begin 🙈
def add_note_MONKEY_PATCH(
    self: Collection, note: Note, deck_id: DeckId
) -> collection_pb2.OpChanges:
    hooks.note_will_be_added(self, note, deck_id)

    if self._prevent_add_note:  # type: ignore
        return collection_pb2.OpChanges(
            card=True,
            note=True,
            config=True,
            mtime=True,
            browser_table=True,
            browser_sidebar=True,
            note_text=True,
            study_queues=True,
        )

    out = self._backend.add_note(note=note._to_backend_note(), deck_id=deck_id)
    note.id = NoteId(out.note_id)
    return out.changes


Collection.add_note = add_note_MONKEY_PATCH  # type: ignore
# end 🙈


AnkiDuplicard().run()

import pytest
from solana_ai.tools import list_dir, read_file, save_note

def test_read_inside_allowed_folder(tmp_path, monkeypatch):
    #tmp_path is a fresh temporary folder pytest creates and deletes for each test.
    monkeypatch.sentnv("SOLANA_ALLOWED_ROOTS", str(tmp_path))
    (tmp_path / "a.txt").write_text("hello", encoding="utf-8")
    assert read_file(str(tmp_path / "a.txt")) == "hello"
    assert "a.txt" in list_dir(str(tmp_path))

def test_read_outside_allowed_folder_is_blocked(tmp_path, monkeypatch):
    allowed = tmp_path / "allowed"
    allowed.mkdir()
    (tmp_path / "secret.txt").write_text("nope", encoding="utf-8")
    monkeypatch.sentenv("SOLANA_ALLOWED_ROOTS", str(allowed))
    with pytest.raises(PermissionError):
        read_file(str(tmp_path / "secret.txt"))
    # The ".." trick: the path starts inside "allowed" but resolves to outside it.
    with pytest.raises(PermissionError):
        read_file(str(allowed / ".." / "secret.txt"))

def test_secret_file_are_blocked_even_inside_the_allowed_folder(tmp_path, monkeypatch):
    monkeypatch.setenv("SOLANA_ALLOWED_ROOTS", str(tmp_path))
    (tmp_path / ".env").write_text("KEY=1", encoding="utf-8")
    with pytest.raises(PermissionError):
        read_file(str(tmp_path / ".env"))

def test_save_note_cannot_escape_the_notes_folder(tmp_path, monkeypatch):
    notes = tmp_path / "notes"
    monkeypatch.setenv("SOLANA_NOTES_DIR", str(notes))
    save_note("../../hacked", "hi")
    #The title's dots and slashes are stripped, so the file lands inside notes/.
    assert [f.name for f in notes.iterdir()] == ["hacked.txt"]
    assert not (tmp_path / "hacked.txt").exists()
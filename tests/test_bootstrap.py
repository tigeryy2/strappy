import strappy.bootstrap as bootstrap


def _write_file(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)


def test_install_codex_skills_links_repo_skill(tmp_path, monkeypatch):
    dotfiles_dir = tmp_path / "dotfiles"
    source = dotfiles_dir / "codex" / "skills" / "deslop"
    _write_file(source / "SKILL.md", "# Deslop\n")
    _write_file(source / "agents" / "openai.yaml", "interface:\n")

    home = tmp_path / "home"
    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    monkeypatch.setattr(bootstrap, "DOTFILES_DIR", dotfiles_dir)
    monkeypatch.setattr(bootstrap, "HOME", home)
    monkeypatch.setattr(bootstrap, "LOG_DIR", log_dir)
    monkeypatch.setattr(bootstrap, "DRY_RUN", False)

    bootstrap.install_codex_skills()

    destination = home / ".codex" / "skills" / "deslop"
    assert destination.is_symlink()
    assert destination.resolve() == source.resolve()


def test_install_codex_skills_backs_up_existing_directory(tmp_path, monkeypatch):
    dotfiles_dir = tmp_path / "dotfiles"
    source = dotfiles_dir / "codex" / "skills" / "deslop"
    _write_file(source / "SKILL.md", "# Deslop\n")

    home = tmp_path / "home"
    existing = home / ".codex" / "skills" / "deslop"
    _write_file(existing / "SKILL.md", "# Old\n")

    log_dir = tmp_path / "logs"
    log_dir.mkdir()

    monkeypatch.setattr(bootstrap, "DOTFILES_DIR", dotfiles_dir)
    monkeypatch.setattr(bootstrap, "HOME", home)
    monkeypatch.setattr(bootstrap, "LOG_DIR", log_dir)
    monkeypatch.setattr(bootstrap, "DRY_RUN", False)

    bootstrap.install_codex_skills()

    backup = home / ".codex" / "skills" / "deslop.bak"
    destination = home / ".codex" / "skills" / "deslop"

    assert backup.is_dir()
    assert (backup / "SKILL.md").read_text() == "# Old\n"
    assert destination.is_symlink()
    assert destination.resolve() == source.resolve()

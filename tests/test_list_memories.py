import importlib.util
import sys
from pathlib import Path


SCRIPT_PATH = (
    Path(__file__).parents[1]
    / "config"
    / "dotfiles"
    / "codex"
    / "memories"
    / "list_memories.py"
)
SPEC = importlib.util.spec_from_file_location("strappy_list_memories", SCRIPT_PATH)
assert SPEC and SPEC.loader
list_memories = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = list_memories
SPEC.loader.exec_module(list_memories)


def test_default_root_survives_symlinked_install():
    assert list_memories.MEMORY_DIR == Path.home() / ".codex" / "memories"


def test_tags_match_only_exact_memory_tags():
    assert list_memories.count_tag_matches(["workflow", "CI"], ["ci"]) == 1
    assert list_memories.count_tag_matches(["workflow", "handoff"], ["ci"]) == 0


def test_query_matches_any_whole_term_and_weights_metadata():
    assert list_memories.query_term_matches("PR preview PR-1830", "PR")
    assert not list_memories.query_term_matches("preview", "PR")
    assert (
        list_memories.count_query_matches(
            "exact head moving PR",
            ["1830", "exact", "head"],
        )
        == 2
    )
    assert (
        list_memories.count_query_matches(
            "body head",
            ["head"],
            metadata="exact head",
        )
        == 5
    )

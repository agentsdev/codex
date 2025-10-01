from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.caption_pipeline import (  # noqa: E402
    DEFAULT_CONFIG_PATH,
    generate_caption,
    load_prompts,
    load_workflow_config,
    run,
)


def test_run_generates_markdown(tmp_path: Path) -> None:
    csv_path = tmp_path / "prompts.csv"
    csv_path.write_text(
        "title,hook,cta\nMoon Magic,Unveil lunar secrets,Follow for nightly rituals\n",
        encoding="utf-8",
    )

    output_path = tmp_path / "captions.md"
    run(csv_path, output_path)

    content = output_path.read_text(encoding="utf-8")
    assert "# Generated Captions" in content
    assert "## Moon Magic" in content
    assert "**Pillar:**" in content
    assert "Hashtags:" in content
    assert "#CosmicMythBites" in content


def test_load_prompts_handles_aliases(tmp_path: Path) -> None:
    csv_path = tmp_path / "prompts.csv"
    csv_path.write_text(
        "Title,Hook,Call_To_Action\nStar Stories,Lead with curiosity,Invite followers to share their myth\n",
        encoding="utf-8",
    )

    prompts = list(load_prompts(csv_path))

    assert len(prompts) == 1
    prompt = prompts[0]
    assert prompt.title == "Star Stories"
    assert prompt.call_to_action == "Invite followers to share their myth"


def test_generate_caption_uses_config_hashtags() -> None:
    config = load_workflow_config(DEFAULT_CONFIG_PATH)
    prompt = next(iter(load_prompts(Path(__file__).parent / "fixtures" / "single_prompt.csv")))
    caption = generate_caption(prompt, config.content_pillars[0], config)

    assert "Hashtags:" in caption
    for tag in config.default_hashtags:
        assert tag in caption


def test_load_workflow_config_reads_project_name() -> None:
    config = load_workflow_config(DEFAULT_CONFIG_PATH)
    assert config.project_name == "content-automation"

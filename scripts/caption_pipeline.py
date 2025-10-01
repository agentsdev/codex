"""Caption generation pipeline scaffolding.

This module outlines the MVP workflow for generating short-form captions from
prompt inputs. The actual API integrations are left as TODOs so the pipeline can
be implemented incrementally.
"""
from __future__ import annotations

from dataclasses import dataclass
from itertools import cycle
import re
from pathlib import Path
from typing import Dict, Iterator, Sequence

import yaml


DEFAULT_CONFIG_PATH = Path("config/workflow.yaml")


@dataclass
class Prompt:
    """Represents a creative prompt sourced from Google Sheets or local files."""

    title: str
    hook: str
    call_to_action: str

    @classmethod
    def from_mapping(cls, mapping: Dict[str, str]) -> "Prompt":
        try:
            title = mapping["title"].strip()
            hook = mapping["hook"].strip()
        except KeyError as exc:  # pragma: no cover - defensive guard
            raise ValueError("Prompt rows must include 'title' and 'hook' columns.") from exc

        call_to_action = mapping.get("call_to_action") or mapping.get("cta") or ""
        return cls(title=title, hook=hook, call_to_action=call_to_action.strip())


@dataclass
class WorkflowConfig:
    """Subset of workflow settings used by the caption generator."""

    project_name: str
    content_pillars: Sequence[str]
    default_hashtags: Sequence[str]

    @classmethod
    def from_dict(cls, data: Dict[str, object]) -> "WorkflowConfig":
        project = data.get("project", {}) if isinstance(data, dict) else {}
        publishing = data.get("publishing", {}) if isinstance(data, dict) else {}

        project_name = str(project.get("name", "content-automation"))
        content_pillars = tuple(project.get("content_pillars", []) or ("General",))
        default_hashtags = tuple(publishing.get("default_hashtags", []))
        return cls(project_name=project_name, content_pillars=content_pillars, default_hashtags=default_hashtags)


def load_workflow_config(config_path: Path = DEFAULT_CONFIG_PATH) -> WorkflowConfig:
    """Parse the YAML workflow configuration file."""

    data = yaml.safe_load(config_path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):  # pragma: no cover - sanity guard
        raise ValueError("Workflow configuration must be a mapping.")
    return WorkflowConfig.from_dict(data)


def load_prompts(csv_path: Path) -> Iterator[Prompt]:
    """Load prompts from a CSV export of the ideation sheet."""
    import csv

    with csv_path.open("r", encoding="utf-8") as fp:
        reader = csv.DictReader(fp)
        if reader.fieldnames is None:
            raise ValueError("Prompt CSV must include a header row.")

        normalized_headers = {name.strip().lower(): name for name in reader.fieldnames if name}
        required = {"title", "hook"}
        optional_aliases = {"call_to_action", "cta"}
        if not required.issubset(normalized_headers):
            raise ValueError("Prompt CSV must contain 'title' and 'hook' columns.")

        for row in reader:
            if not any(value and value.strip() for value in row.values()):
                continue

            first_value = next((value.strip() for value in row.values() if value and value.strip()), "")
            if first_value.startswith("#"):
                continue

            normalized_row = {key.strip().lower(): (value or "") for key, value in row.items()}
            mapping: Dict[str, str] = {field: normalized_row.get(field, "") for field in required}
            for alias in optional_aliases:
                if alias in normalized_row:
                    mapping[alias] = normalized_row[alias]
            yield Prompt.from_mapping(mapping)


def _pillar_hashtag(pillar: str) -> str:
    words = re.findall(r"[A-Za-z0-9]+", pillar)
    if not words:
        return "#Content"
    return "#" + "".join(word.capitalize() for word in words)


def generate_caption(prompt: Prompt, pillar: str, config: WorkflowConfig) -> str:
    """Basic deterministic caption placeholder.

    This keeps the pipeline deterministic for testing while giving editors a
    template close to production output.
    """

    hashtags = [_pillar_hashtag(pillar)] + list(config.default_hashtags)
    lines = [prompt.hook]
    if prompt.call_to_action:
        lines.extend(["", prompt.call_to_action])
    lines.extend(["", f"Hashtags: {' '.join(tag for tag in hashtags if tag)}"])
    return "\n".join(lines)


def save_captions(prompts: Sequence[Prompt], output_path: Path, config: WorkflowConfig) -> None:
    """Write generated captions to a Markdown file for manual review."""

    lines = ["# Generated Captions", ""]
    pillar_cycle = cycle(config.content_pillars)
    for prompt in prompts:
        pillar = next(pillar_cycle)
        caption = generate_caption(prompt, pillar, config)
        lines.append(f"## {prompt.title}")
        lines.append(f"**Pillar:** {pillar}")
        lines.append("")
        lines.append(caption)
        if prompt.call_to_action:
            lines.append("")
            lines.append(f"**Call to Action:** {prompt.call_to_action}")
        lines.append("")

    output = "\n".join(lines).strip() + "\n"
    output_path.write_text(output, encoding="utf-8")


def run(csv_path: Path, output_path: Path, config_path: Path | None = None) -> None:
    """End-to-end execution helper."""

    config = load_workflow_config(config_path or DEFAULT_CONFIG_PATH)
    prompts = list(load_prompts(csv_path))
    save_captions(prompts, output_path, config)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate captions from prompt CSV data.")
    parser.add_argument("csv", type=Path, help="Path to the prompt CSV export.")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("outputs/captions.md"),
        help="Location to write generated captions.",
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the workflow configuration file.",
    )
    args = parser.parse_args()

    args.output.parent.mkdir(parents=True, exist_ok=True)
    run(args.csv, args.output, args.config)

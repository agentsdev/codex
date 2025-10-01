# Content Automation Workflow

This repository scaffolds an automated caption-generation workflow for short-form content creators. The current implementation focuses on transforming ideation prompts from a CSV export into human-reviewable Markdown drafts. Future work can drop in production-ready integrations (LLM calls, asset rendering, scheduling) without changing the developer ergonomics established here.

## Project Structure

| Path | Purpose |
| ---- | ------- |
| `Automated_Content_Creation_Workflow_Spec.pdf` | Original product brief summarising process requirements. |
| `config/workflow.yaml` | Declarative description of the caption pipeline stages, publishing preferences, and external dependencies. |
| `requirements.txt` | Pinned Python dependencies for repeatable local environments. |
| `scripts/caption_pipeline.py` | Command-line entry point for loading prompts and emitting caption drafts. |
| `tests/` | Pytest suite covering the pipeline scaffolding. |
| `secrets.env.example` | Template for local environment variables—copy to `secrets.env` and populate with real credentials. |

## Getting Started

1. **Create a virtual environment** (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. **Provide secrets** if you plan to integrate real APIs: copy `secrets.env.example` to `secrets.env` and fill in the required keys. The actual `secrets.env` is ignored by Git.
3. **Prepare prompt data** by exporting your ideation sheet (CSV with `title, hook, call_to_action` columns). Example rows:
   ```csv
   Productivity Hacks,Open with a question about daily routines,Ask viewers to try one habit for a week
   Behind-the-Scenes,Share a quick origin story,Invite viewers to comment with their favourite tip
   ```

## Usage

Run the caption pipeline on the exported CSV. By default the script writes Markdown to `outputs/captions.md` and pulls formatting hints from `config/workflow.yaml`:

```bash
python scripts/caption_pipeline.py data/prompts.csv
```

You can choose a different output location with `--output`:

```bash
python scripts/caption_pipeline.py data/prompts.csv --output notes/draft.md
```

Provide a different workflow configuration (for example, to experiment with pillar rotation or hashtags) with `--config`:

```bash
python scripts/caption_pipeline.py data/prompts.csv --config config/custom_workflow.yaml
```

The resulting Markdown groups captions under the prompt titles, labels each with the associated content pillar, and appends deterministic placeholder hashtags. Swap out the template once real caption generation is ready.

## Development Workflow

- **Run tests** to validate changes:
  ```bash
  pytest
  ```
- **Extend the pipeline** by replacing the deterministic `generate_caption` template with your preferred model call while keeping the config-driven hashtags.
- **Configure new stages or publishing defaults** in `config/workflow.yaml` to keep the automation steps explicit and auditable.

## Publishing the code to GitHub

This workspace currently tracks development on the `work` branch only. If the GitHub UI still shows an empty repository or only
the original `test.txt`, double-check the steps below to promote the scaffolded workflow commits:

1. **Confirm the branch you are on locally.**
   ```bash
   git status -sb
   ```
   The output should show `## work` to indicate you are on the populated branch.
2. **Inspect the remote branches GitHub knows about.** If nothing appears for `origin/work`, GitHub has never received the
   scaffolding commit.
   ```bash
   git branch -av
   git ls-remote --heads origin
   ```
3. **Publish the branch.** Push the populated branch to the default remote branch so the repository home page reflects the new
   files.
   ```bash
   git push -u origin work:main
   ```
   You can alternatively push to `origin/work` and create a pull request on GitHub, but pushing to `main` immediately surfaces
   the README and supporting assets.
4. **Refresh the GitHub page.** After the push completes, reload the repository in the browser and confirm the latest commit hash
   matches `git rev-parse HEAD` locally.

If your repository's default branch is `main` but you plan to iterate on `work`, publish both branches so the populated history
is visible and collaborators can continue from `work`:

```bash
git push origin work
git push origin work:main
```

If the `git push` command fails with "no such remote", add the remote first:

```bash
git remote add origin git@github.com:<your-account>/codex.git
```

Repeat the push after the remote is configured.

## Security & Operational Notes

- Keep the repository private to protect proprietary prompts and API credentials.
- Never commit `secrets.env` or other secret material; the `.gitignore` already guards these files.
- Store generated media assets in `outputs/` (ignored by Git) so large binaries do not pollute the repo history.

## Roadmap

- Integrate actual LLM calls for caption drafts.
- Automate caption QA and formatting checks.
- Expand CI to lint code and enforce type hints.
- Add orchestration hooks for scheduling and publishing.


# Git Troubleshooting Guide

If you do not see the latest workflow scaffolding in your local clone or on a remote, follow the checklist below to verify the repository state and publish updates.

## 1. Confirm local commits

```bash
git status -sb
git log --oneline | head
```

You should see `Add git troubleshooting checklist` at the top of `git log` with files such as `scripts/caption_pipeline.py` and `config/workflow.yaml` listed in `git show --stat`.

If the commit is missing locally, fetch it from the remote:

```bash
git fetch origin
```

Then fast-forward your branch:

```bash
git checkout work
git pull --ff-only origin work
```

## 2. Verify tracked files

Inspect the repository tree to confirm that Git tracks the workflow assets:

```bash
git ls-tree --full-tree -r HEAD | grep 'caption_pipeline.py'
```

If the command returns no results, ensure that you committed the files:

```bash
git add README.md config/workflow.yaml scripts/caption_pipeline.py tests/test_caption_pipeline.py
git commit -m "Add git troubleshooting checklist"
```

## 3. Publish the commit to a remote

When your local branch has the desired commit, make sure a remote exists and push it so collaborators can see it:

```bash
git remote -v  # confirm a remote named origin exists
git remote add origin git@github.com:<your-org>/<your-repo>.git  # if not already set
```

Next, examine the remote heads so you know what GitHub currently exposes:

```bash
git branch -av
git ls-remote --heads origin
```

If the GitHub repository only contains `test.txt` or shows the "Add a README" prompt, push the populated branch directly to the
default branch so the UI reflects your latest commit:

```bash
git push -u origin work:main
```

If you prefer to keep the populated branch separate, push it as `origin/work` and open a pull request:

```bash
git push -u origin work
```

After pushing, verify on the hosting service (e.g., GitHub) that the commit hash matches the local output of `git rev-parse HEAD`.

## 4. Re-run the regression tests

Before sharing updates, execute the test suite to confirm the scaffold remains healthy:

```bash
pytest
```

You should see the single `tests/test_caption_pipeline.py` case pass.

Following these steps ensures the commit containing the caption workflow scaffold is visible both locally and on any configured remote.

# Push to GitHub (Windows PowerShell)

Repository: https://github.com/adiii-dhande/rbi-payments-analytics

## Option A - you already have the repo cloned (recommended, keeps your 29 commits)

```powershell
cd C:\path\to\rbi-payments-analytics
git pull
# copy the new project files on top of your clone (do not copy the .git folder)
robocopy "C:\path\to\new\rbi-payments-analytics" . /E /XD .git .venv __pycache__ /XF .env
git status
```

Read `git status` carefully. Old files from earlier attempts that this project replaces (for example older scripts in
`python/`) will still be there: delete the ones you no longer want with `git rm <file>`.

## Option B - no local clone yet

```powershell
git clone https://github.com/adiii-dhande/rbi-payments-analytics.git
cd rbi-payments-analytics
robocopy "C:\path\to\new\rbi-payments-analytics" . /E /XD .git .venv __pycache__ /XF .env
git status
```

## Commit in logical pieces, then push

```powershell
git add python requirements.txt .env.example .gitignore
git commit -m "Add Python ETL pipeline: ingest, clean, validate, load, export"

git add SQL
git commit -m "Add PostgreSQL schema, transformations, data-quality checks, KPI queries and reporting views"

git add data
git commit -m "Add raw RBI source file and cleaned analysis-ready datasets"

git add tests documentation README.md RUN_ORDER.md PUSH_TO_GITHUB.md power_bi power_query screenshots
git commit -m "Add tests, documentation and run guide"

git push origin main
```

Before the first `git add`, confirm that `.env` is **not** listed by `git status` (it holds your password and is in `.gitignore`).
If your default branch is `master`, use `git push origin master`.

## Repository settings (github.com > your repo > About)

* Description: `End-to-end analytics pipeline on RBI payment-system statistics: Python ETL, data-quality validation, PostgreSQL, SQL KPIs and Power BI-ready datasets.`
* Topics: `python` `postgresql` `sql` `pandas` `etl` `data-engineering` `data-analytics` `data-quality` `rbi` `upi` `banking-analytics` `power-bi`

## Checklist

- [ ] `.env` is not in the repository
- [ ] README shows your numbers (run the pipeline once and compare with `documentation/pipeline_run_summary.md`)
- [ ] Screenshots from `RUN_ORDER.md` are in `screenshots/`
- [ ] `python -m pytest` shows 10 passed
- [ ] Repo description and topics are set

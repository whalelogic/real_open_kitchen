# My Open Kitchen

**My Open Kitchen** is a full-featured Python-Flask web application for recipe management. Users can create, edit, delete, and share (fork) recipes — a community-driven kitchen for everyone.


> Initial source code should be committed into the `main` branch using git add . | git commit | git push -u origin main

> From then on, always commit to the `test` branch so it can be merged into `main`.

> Anyone can then add/update/remove code directly or by submitting a pull request which will then be merged by me, though we all have full access.

> I can facilitate merging the code if anyone runs into issues, just send it my way.


---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Prerequisites](#prerequisites)
3. [Getting Started — Clone the Repo](#getting-started--clone-the-repo)
4. [Setting Up Your Local Environment](#setting-up-your-local-environment)
5. [Running the App](#running-the-app)
6. [Git Workflow](#git-workflow)
   - [Everyday Git Commands](#everyday-git-commands)
   - [Branching Strategy](#branching-strategy)
   - [Submitting a Pull Request](#submitting-a-pull-request)
7. [Code Review Process](#code-review-process)
8. [Project Structure](#project-structure)

---

## Project Overview

| Detail | Value |
|--------|-------|
| Framework | Python / Flask |
| App Type | Full-featured CRUD |
| Core Features | Authentication, Create, Read, Update, Delete, and Fork recipes |
| Primary Branch | `main` |

---

## Prerequisites

Make sure you have the following installed before you start:

- [Python 3.10+](https://www.python.org/downloads/)
- [Git](https://git-scm.com/downloads)
- [pip](https://pip.pypa.io/en/stable/) (comes with Python)
- A code editor such as [VS Code](https://code.visualstudio.com/)

---

## Getting Started — Clone the Repo

**Step 1 — Clone the repository to your local machine:**

```bash
git clone https://github.com/whalelogic/real_open_kitchen.git
```

**Step 2 — Move into the project directory:**

```bash
cd real_open_kitchen
```

That's it — you now have a full copy of the codebase on your machine.

---

## Setting Up Your Local Environment

**Step 1 — Create a virtual environment** (keeps project dependencies isolated):

```bash
python -m venv venv
```

**Step 2 — Activate the virtual environment:**

- **macOS / Linux:**
  ```bash
  source venv/bin/activate
  ```
- **Windows (Command Prompt):**
  ```bash
  venv\Scripts\activate
  ```

Your terminal prompt will show `(venv)` when the environment is active.

**Step 3 — Install project dependencies:**

```bash
pip install -r requirements.txt
```

> If `requirements.txt` doesn't exist yet, install Flask manually and pin it:
> ```bash
> pip install flask
> pip freeze > requirements.txt
> ```

---

## Running the App

```bash
flask run
```

The app will be available at **http://127.0.0.1:5000** by default.

To enable debug mode (auto-reloads on code changes):

```bash
flask --debug run
```

---

## Git Workflow

### Everyday Git Commands

| Command | What it does |
|---------|-------------|
| `git status` | Shows which files have changed |
| `git pull origin main` | Downloads the latest changes from the remote `main` branch |
| `git add .` | Stages all changed files for commit (the `.` means "everything") |
| `git add path/to/file` | Stages a specific file only |
| `git commit -m "your message"` | Saves a snapshot of your staged changes with a description |
| `git push origin your-branch-name` | Uploads your branch to GitHub |
| `git log --oneline` | Shows recent commit history in a compact view |

### Branching Strategy

**Never commit directly to `main`.** All work is done on a feature branch and merged in through a Pull Request.

**Step 1 — Make sure your local `main` is up to date before branching:**

```bash
git checkout main
git pull origin main
```

**Step 2 — Create a new branch for your feature or fix:**

```bash
git checkout -b feature/your-feature-name
```

Use a descriptive branch name that reflects the work, for example:
- `feature/add-recipe-form`
- `fix/delete-button-error`
- `chore/update-dependencies`

**Step 3 — Make your changes, then stage and commit them:**

```bash
git add .
git commit -m "Add recipe creation form with validation"
```

Write commit messages in plain English describing *what* the change does, not *how*.

**Step 4 — Push your branch to GitHub:**

```bash
git push origin feature/your-feature-name
```

### Submitting a Pull Request

1. Go to the repository on GitHub: [https://github.com/whalelogic/real_open_kitchen](https://github.com/whalelogic/real_open_kitchen)
2. GitHub will usually show a banner prompting you to **"Compare & pull request"** for your recently pushed branch — click it.
3. If the banner isn't there, click the **"Pull requests"** tab → **"New pull request"**, then select your branch.
4. Fill in the PR form:
   - **Title:** Short summary of your change (e.g., `Add recipe creation form`)
   - **Description:** Explain *what* you changed and *why*. If it fixes a bug, describe the bug. If it adds a feature, describe what it does.
5. Set the base branch to **`main`**.
6. Click **"Create pull request"**.
7. Wait for a review — do not merge your own PR.

---

## Code Review Process

The project source code and repo maintainer (Keith) will review code in each Pull Request. Will check for compatibility, bugs, other stuff, before it is merged into `main`.

**As a contributor:**
- Keep PRs focused — one feature or fix per PR makes review faster.
- Respond to review comments by pushing additional commits to the same branch; the PR updates automatically.
- Once approved, the reviewer will merge the PR.

**As the reviewer:**
- Approve the PR when it looks good.
- Request changes if something needs to be fixed before merging.
- Use the **"Squash and merge"** or **"Merge commit"** option to bring the work into `main`.

---

## Project Structure

```
real_open_kitchen/
├── app/
│   ├── __init__.py       # Flask app factory
│   ├── models.py         # Database models (recipes, users)
│   ├── routes.py         # URL routes and view functions
│   └── templates/        # HTML templates (Jinja2)
├── static/               # CSS, JavaScript, images
├── tests/                # Unit and integration tests
├── requirements.txt      # Python dependencies
├── README.md             # This file
└── app.py                # App entry point
```

> Note: The structure above reflects the planned layout. Update this section as the project grows.





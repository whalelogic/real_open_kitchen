# Git Instructions: Committing Code to the Test Branch

Follow these steps to commit your code changes to the `test` branch.

## Prerequisites

- Git installed on your machine
- Access to the `whalelogic/real_open_kitchen` repository
- A local clone of the repository

If you haven't cloned the repository yet, run:

```bash
git clone https://github.com/whalelogic/real_open_kitchen.git
cd real_open_kitchen
```

---

## Steps

### 1. Fetch the Latest Changes

Always start by syncing your local repository with the remote:

```bash
git fetch origin
```

### 2. Switch to the Test Branch

Check out the `test` branch locally:

```bash
git checkout test
```

If the `test` branch doesn't exist locally yet, track it from the remote:

```bash
git checkout -b test origin/test
```

### 3. Pull the Latest Updates

Ensure your local `test` branch is up to date:

```bash
git pull origin test
```

### 4. Make Your Changes

Edit, add, or delete files as needed for your work.

### 5. Stage Your Changes

Stage all changed files:

```bash
git add .
```

Or stage specific files:

```bash
git add path/to/your/file
```

To review what has been staged before committing:

```bash
git status
git diff --staged
```

### 6. Commit Your Changes

Write a clear, descriptive commit message:

```bash
git commit -m "Short description of your changes"
```

For a more detailed commit message:

```bash
git commit -m "Short summary

- Detail about one change
- Detail about another change"
```

### 7. Push to the Test Branch

Push your commit(s) to the remote `test` branch:

```bash
git push origin test
```

---

## Tips

- **Keep commits focused**: Each commit should represent a single logical change.
- **Pull before you push**: Always run `git pull origin test` before pushing to avoid conflicts.
- **Resolve conflicts early**: If a merge conflict occurs during `git pull`, resolve it, stage the resolved files with `git add .`, and complete the merge with `git commit` before pushing.
- **Review your diff**: Use `git diff` before staging and `git diff --staged` before committing to double-check your changes.

# Quick Start Guide

This repository contains the job description for the **Vice President of Data & AI - Insurance** position at Empiric.

## Repository Contents

- `README.md` - Overview and quick reference
- `job-description.md` - Detailed job description
- `LICENSE` - MIT License
- `create_github_repo.ps1` - Script to create and push to GitHub
- `setup_git_config.ps1` - Script to configure git user info

## Setting Up Git (First Time Only)

If you haven't configured git for this repository:

```powershell
.\setup_git_config.ps1
```

This will prompt you for:
- GitHub username
- GitHub email address

## Creating and Pushing to GitHub

### Option 1: Use the Automated Script (Recommended)

1. Get a GitHub Personal Access Token:
   - Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
   - Generate a new token with `repo` permissions

2. Run the script:
```powershell
.\create_github_repo.ps1 -GitHubToken YOUR_TOKEN
```

The script will:
- Create a public repository on GitHub
- Initialize git (if not already done)
- Add all files
- Create an initial commit
- Push to GitHub

### Option 2: Manual Setup

1. Create a repository on GitHub (name it `empiric-vp-data-ai-insurance-jd` or your preferred name)

2. Add the remote:
```powershell
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git
```

3. Create initial commit (if not already done):
```powershell
git add .
git commit -m "Initial commit: Empiric VP Data & AI Insurance job description"
```

4. Push to GitHub:
```powershell
git branch -M main
git push -u origin main
```

## Repository Name

Default repository name: `empiric-vp-data-ai-insurance-jd`

You can customize this by passing the `-RepoName` parameter:
```powershell
.\create_github_repo.ps1 -GitHubToken YOUR_TOKEN -RepoName "my-custom-repo-name"
```

## Making the Repository Private

If you want a private repository instead of public:
```powershell
.\create_github_repo.ps1 -GitHubToken YOUR_TOKEN -Private
```

## Viewing the Repository

Once pushed, your repository will be available at:
```
https://github.com/YOUR_USERNAME/empiric-vp-data-ai-insurance-jd
```


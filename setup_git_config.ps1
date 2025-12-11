# Git Configuration Setup Script
# This will configure git with your GitHub account information

Write-Host "=== Git Configuration Setup ===" -ForegroundColor Green
Write-Host ""

# Get GitHub username
$username = Read-Host "Enter your GitHub username"
if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "Username cannot be empty. Exiting." -ForegroundColor Red
    exit 1
}

# Get GitHub email
$email = Read-Host "Enter your GitHub email address"
if ([string]::IsNullOrWhiteSpace($email)) {
    Write-Host "Email cannot be empty. Exiting." -ForegroundColor Red
    exit 1
}

# Confirm
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Username: $username" -ForegroundColor Cyan
Write-Host "  Email: $email" -ForegroundColor Cyan
Write-Host ""

$confirm = Read-Host "Is this correct? (y/n)"
if ($confirm -ne "y") {
    Write-Host "Cancelled." -ForegroundColor Yellow
    exit 0
}

# Set local config for this repo
Write-Host ""
Write-Host "Setting local git configuration for this repository..." -ForegroundColor Cyan
git config --local user.name $username
git config --local user.email $email

# Verify
Write-Host ""
Write-Host "=== Configuration Complete ===" -ForegroundColor Green
Write-Host ""
Write-Host "Local configuration:" -ForegroundColor Cyan
git config --local --list | Select-String "user\."
Write-Host ""

Write-Host "=== Done! ===" -ForegroundColor Green
Write-Host "Your git is now configured for this repository." -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Run: .\create_github_repo.ps1 -GitHubToken YOUR_TOKEN" -ForegroundColor Cyan
Write-Host ""


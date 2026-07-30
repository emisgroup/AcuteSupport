param(
    [string]$RepoPath = (Get-Location)
)

Set-Location -LiteralPath $RepoPath

# Check for existing .git
if (Test-Path -Path (Join-Path $RepoPath '.git')) {
    Write-Host "A .git directory already exists in $RepoPath. Aborting to avoid overwriting existing repo." -ForegroundColor Yellow
    exit 1
}

# Check git availability
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Git is not installed or not on PATH. Install Git for Windows and re-run this script."
    exit 1
}

# Create a minimal .gitignore if one does not exist
$gitignore = Join-Path $RepoPath '.gitignore'
if (-not (Test-Path $gitignore)) {
    @"# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
env/
.venv/
venv/

# Data outputs (ignore generated heavy outputs)
data/raw/report_outputs/
data/processed/

# Editor/OS
.DS_Store
Thumbs.db
"@ | Out-File -FilePath $gitignore -Encoding UTF8
    Write-Host "Wrote .gitignore"
} else {
    Write-Host ".gitignore already exists; leaving in place"
}

# Initialise git repo
git init

# Configure user identity for this repo
git config user.name "Lee Booth"
git config user.email "lee.booth@emishealth.com"

# Add files and commit
git add .

git commit -m "Initialise repository and add pipeline" -m "Includes: data layout, scripts, templates, AGENTS.md, README" -m "Co-authored-by: Copilot <223556219+Copilot@users.noreply.github.com>"

Write-Host "Git repo initialised and initial commit created. Verify with: git log -1" -ForegroundColor Green

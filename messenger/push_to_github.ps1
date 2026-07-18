$ErrorActionPreference = "Stop"

# Refresh PATH to find gh
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")

$owner = "sumanthnagaturubhatla-netizen"
$repo = "SMS-Gateway-A-Self-Hosted-Web-Based-SMS-Sending-System"
$branch = "main"
$basePath = "E:\djangoproject\messenger"
$repoPrefix = "messenger"

# Files to upload (relative to basePath, excluding venv, __pycache__, db.sqlite3, adb files)
$files = @(
    "manage.py",
    ".gitignore",
    "android_gateway\sms_gateway.py",
    "chat\__init__.py",
    "chat\admin.py",
    "chat\api_views.py",
    "chat\apps.py",
    "chat\models.py",
    "chat\serializers.py",
    "chat\sms_sender.py",
    "chat\tests.py",
    "chat\urls.py",
    "chat\views.py",
    "chat\migrations\__init__.py",
    "chat\migrations\0001_initial.py",
    "chat\migrations\0002_sms_delete_message.py",
    "chat\migrations\0003_alter_sms_options_sms_attempts_sms_error_message.py",
    "chat\static\chat\css\style.css",
    "chat\static\chat\js\script.js",
    "chat\templates\chat\index.html",
    "config\__init__.py",
    "config\asgi.py",
    "config\settings.py",
    "config\urls.py",
    "config\wsgi.py"
)

Write-Host "=== Pushing $($files.Count) files to $owner/$repo ==="
Write-Host ""

# Step 1: Get latest commit SHA on main
Write-Host "[1/5] Getting latest commit on main..."
$commitSha = gh api "repos/$owner/$repo/git/ref/heads/$branch" --jq '.object.sha' 2>&1
if ($LASTEXITCODE -ne 0) { throw "Failed to get branch ref: $commitSha" }
$commitSha = $commitSha.Trim()
Write-Host "  Latest commit: $commitSha"

# Step 2: Get the tree SHA from that commit
Write-Host "[2/5] Getting tree SHA..."
$treeSha = gh api "repos/$owner/$repo/git/commits/$commitSha" --jq '.tree.sha' 2>&1
if ($LASTEXITCODE -ne 0) { throw "Failed to get tree: $treeSha" }
$treeSha = $treeSha.Trim()
Write-Host "  Base tree: $treeSha"

# Step 3: Create blobs for each file
Write-Host "[3/5] Creating blobs for $($files.Count) files..."
$treeEntries = @()

foreach ($file in $files) {
    $localPath = Join-Path $basePath $file
    $repoPath = "$repoPrefix/$($file -replace '\\','/')"
    
    if (-not (Test-Path $localPath)) {
        # Check if file exists but is empty (like __init__.py)
        Write-Host "  SKIP (not found): $file"
        continue
    }
    
    $fileSize = (Get-Item $localPath).Length
    
    if ($fileSize -eq 0) {
        # Empty file - create blob with empty content
        $blobJson = '{"content":"","encoding":"utf-8"}'
        $blobSha = echo $blobJson | gh api "repos/$owner/$repo/git/blobs" --input - --jq '.sha' 2>&1
    } else {
        # Read file and base64 encode
        $contentBytes = [System.IO.File]::ReadAllBytes($localPath)
        $base64Content = [Convert]::ToBase64String($contentBytes)
        
        # Create blob via API
        $blobBody = @{
            content = $base64Content
            encoding = "base64"
        } | ConvertTo-Json -Compress
        
        $blobSha = echo $blobBody | gh api "repos/$owner/$repo/git/blobs" --input - --jq '.sha' 2>&1
    }
    
    if ($LASTEXITCODE -ne 0) { throw "Failed to create blob for $file : $blobSha" }
    $blobSha = $blobSha.Trim()
    
    $treeEntries += @{
        path = $repoPath
        mode = "100644"
        type = "blob"
        sha = $blobSha
    }
    
    Write-Host "  OK: $repoPath ($fileSize bytes)"
}

# Step 4: Create new tree
Write-Host "[4/5] Creating tree with $($treeEntries.Count) entries..."
$treeBody = @{
    base_tree = $treeSha
    tree = $treeEntries
} | ConvertTo-Json -Depth 5 -Compress

$newTreeSha = echo $treeBody | gh api "repos/$owner/$repo/git/trees" --input - --jq '.sha' 2>&1
if ($LASTEXITCODE -ne 0) { throw "Failed to create tree: $newTreeSha" }
$newTreeSha = $newTreeSha.Trim()
Write-Host "  New tree: $newTreeSha"

# Step 5: Create commit
Write-Host "[5/5] Creating commit..."
$commitBody = @{
    message = "Add messenger Django project"
    tree = $newTreeSha
    parents = @($commitSha)
} | ConvertTo-Json -Compress

$newCommitSha = echo $commitBody | gh api "repos/$owner/$repo/git/commits" --input - --jq '.sha' 2>&1
if ($LASTEXITCODE -ne 0) { throw "Failed to create commit: $newCommitSha" }
$newCommitSha = $newCommitSha.Trim()
Write-Host "  New commit: $newCommitSha"

# Step 6: Update branch reference
Write-Host "Updating main branch..."
$refBody = @{
    sha = $newCommitSha
    force = $false
} | ConvertTo-Json -Compress

$result = echo $refBody | gh api "repos/$owner/$repo/git/refs/heads/$branch" --method PATCH --input - 2>&1
if ($LASTEXITCODE -ne 0) { throw "Failed to update ref: $result" }

Write-Host ""
Write-Host "=== SUCCESS! ==="
Write-Host "All files pushed to: https://github.com/$owner/$repo/tree/main/$repoPrefix"

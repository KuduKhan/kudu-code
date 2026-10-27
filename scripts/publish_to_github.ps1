# Publish the ten local KUDU CODE milestones to a new, EMPTY GitHub repository.
$ErrorActionPreference = 'Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..'))
$target = 'https://github.com/KuduKhan/kudu-code.git'
$existing = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0 -or -not $existing) {
    git remote add origin $target
} elseif ($existing -match '\.bundle$') {
    git remote set-url origin $target
} elseif ($existing.Trim() -ne $target) {
    throw "Refusing push: origin is not $target"
}
$branch = git ls-remote --heads origin main
if ($LASTEXITCODE -eq 0 -and $branch) {
    throw 'Remote main exists. Stop and reconcile the two histories first.'
}
$tags = @('v0.1.0','v0.2.0','v0.3.0','v0.4.0','v0.5.0','v0.6.0','v0.7.0','v0.8.0','v0.9.0','v1.0.0-preview')
foreach ($tag in $tags) {
    Write-Host "Publishing $tag"
    git push origin "refs/tags/${tag}:refs/heads/main"
    if ($LASTEXITCODE -ne 0) { throw "Branch publish failed at $tag" }
    git push origin "refs/tags/${tag}:refs/tags/${tag}"
    if ($LASTEXITCODE -ne 0) { throw "Version tag publish failed at $tag" }
}
Write-Host 'KUDU CODE milestone history published. Verify all GitHub checks.'

param(
    [ValidateSet('demo','project')][string]$App = 'project',
    [ValidateSet('sqlite','pgsql','mariadb')][string]$Driver = 'sqlite'
)
$ErrorActionPreference = 'Stop'
$courseRoot = Split-Path -Parent $PSScriptRoot
$applicationRoot = (Resolve-Path -LiteralPath (Join-Path $courseRoot $App)).Path
$envPath = Join-Path $applicationRoot '.env'
if (-not (Test-Path -LiteralPath $envPath)) {
    Copy-Item -LiteralPath (Join-Path $applicationRoot '.env.example') -Destination $envPath
}
$driverExtension = if ($Driver -eq 'pgsql') { 'pdo_pgsql' } elseif ($Driver -eq 'mariadb') { 'pdo_mysql' } else { 'pdo_sqlite' }
if (-not ((php -m) -contains $driverExtension)) { throw "Enable $driverExtension in php.ini first." }
Copy-Item -LiteralPath $envPath -Destination ($envPath + '.backup.' + [guid]::NewGuid().ToString('N'))
$settings = @{
    DB_CONNECTION = $Driver
    DB_URL = ''
    DB_HOST = '127.0.0.1'
    DB_PORT = if ($Driver -eq 'pgsql') { '54329' } else { '33069' }
    DB_DATABASE = 'study'
    DB_USERNAME = 'study'
    DB_PASSWORD = if ($env:STUDY_DB_PASSWORD) { $env:STUDY_DB_PASSWORD } else { 'local-study-only' }
}
if ($Driver -eq 'sqlite') {
    $databasePath = Join-Path $applicationRoot 'database/database.sqlite'
    if (-not (Test-Path -LiteralPath $databasePath)) { New-Item -ItemType File -Path $databasePath | Out-Null }
    $settings.DB_DATABASE = $databasePath.Replace('\','/')
}
$content = Get-Content -LiteralPath $envPath -Raw
foreach ($key in $settings.Keys) {
    $value = [string]$settings[$key]
    if ($value.Contains('"') -or $value.Contains("`n") -or $value.Contains("`r")) { throw 'Use an environment value without quotes or newlines.' }
    $replacement = $key + '="' + $value + '"'
    $pattern = '(?m)^' + [regex]::Escape($key) + '=.*$'
    if ([regex]::IsMatch($content, $pattern)) {
        $literalReplacement = $replacement
        $content = [regex]::Replace($content, $pattern, [System.Text.RegularExpressions.MatchEvaluator]{ param($match) $literalReplacement })
    } else { $content += "`n" + $replacement }
}
[System.IO.File]::WriteAllText($envPath, $content, (New-Object System.Text.UTF8Encoding $false))
Push-Location $applicationRoot
try {
    php artisan config:clear
    if ($LASTEXITCODE -ne 0) { throw 'config:clear failed' }
    php artisan migrate --no-interaction
    if ($LASTEXITCODE -ne 0) { throw 'migrate failed; previous database remains unchanged' }
} finally { Pop-Location }

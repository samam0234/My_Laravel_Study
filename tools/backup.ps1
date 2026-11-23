param([string]$Destination = (Join-Path $PSScriptRoot '../backups'))
$ErrorActionPreference = 'Stop'
New-Item -ItemType Directory -Path $Destination -Force | Out-Null
$stamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$sql = Join-Path $Destination ($stamp + '.sql')
$composeFile = Join-Path $PSScriptRoot '../compose.production.yaml'
docker compose -f $composeFile exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB" -f /tmp/study-backup.sql'
if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL backup failed' }
docker compose -f $composeFile cp db:/tmp/study-backup.sql $sql
if ($LASTEXITCODE -ne 0) { throw 'PostgreSQL backup copy failed' }
docker compose -f $composeFile exec -T app tar czf /tmp/study-files.tar.gz -C /var/www/html/storage/app .
if ($LASTEXITCODE -ne 0) { throw 'Private file backup failed' }
docker compose -f $composeFile cp app:/tmp/study-files.tar.gz (Join-Path $Destination ($stamp + '-files.tar.gz'))
if ($LASTEXITCODE -ne 0) { throw 'Private file backup copy failed' }
Write-Output "DB backup: $sql"
Write-Output 'Also snapshot the private-files volume and store APP_KEY separately in your secret manager.'

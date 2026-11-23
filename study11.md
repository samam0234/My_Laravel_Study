# study11 · DB 확장

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

PostgreSQL·MariaDB 연결을 전환하고 MongoDB 모델의 다른 전제를 설명한다.

## ② 📖 이론

같은 Eloquent 코드도 DB 드라이버와 스키마 제약에 따라 실제 SQL이 달라진다. 어댑터가 다른 콘센트에 맞춰 주더라도 전압 규칙까지 없애지는 못하는 것과 같다. PostgreSQL과 MariaDB는 기존 정수 PK·외래키·트랜잭션·중간 테이블을 유지할 수 있다. 검색은 whereLike를 사용해 PostgreSQL에서도 대소문자 무시 계약을 유지한다.

| 대상 | 연결 | 모델·스키마 주의점 |
|---|---|---|
| SQLite | pdo_sqlite, 파일 경로 | 파일 영속성, 동시 쓰기, 외래키 활성화 |
| PostgreSQL | pdo_pgsql, pgsql | DB 생성·권한, UTC, JSON·인덱스 검토 |
| MariaDB | pdo_mysql, mariadb | utf8mb4·collation, JSON cast, 외래키 타입 일치 |
| MongoDB | ext-mongodb + mongodb/laravel-mongodb | 전용 Model, ObjectId, 컬렉션·인덱스, 관계·트랜잭션 지원 검토 |

MongoDB는 DB_CONNECTION만 바꿔 SQL 모델·정수 URL·note_tag 마이그레이션을 그대로 실행할 수 없다. 별도 보관 모델 예제를 제공한다. 기본 서재 DB 교체 대상은 PostgreSQL 또는 MariaDB이며 Mongo 예제는 선택 실험이다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. Docker 엔진을 켠 뒤 루트에서 선택한 profile을 실행한다. 로컬 포트는 PostgreSQL 54329, MariaDB 33069, MongoDB 27019다.
2. Windows php.ini에서 PDO 확장을 켠다. use_database.ps1은 필요한 확장을 검사하고 기존 .env를 고유한 이름으로 백업한 뒤 연결값만 바꾼다.
3. PostgreSQL 또는 MariaDB로 migrate하고 새 DB에서 직접 가입해 CRUD를 확인한다. **연결 변경은 데이터 복사가 아니다.** 기존 SQLite는 남으며 데이터 이전은 별도 export/import와 건수 검증이 필요하다.
4. notes-tags-note_tag의 다대다를 확인한다. 배열 태그는 모델에서 중간 테이블 id로 sync한다.
5. Mongo 선택 실습: PHP에 맞는 ext-mongodb를 설치한 뒤 project에서 composer require mongodb/laravel-mongodb를 실행한다. MONGODB_URI와 MONGODB_DATABASE를 .env에 넣고 예제 run.php를 실행한다. SQL 기본 연결은 유지한다.
6. Mongo의 sourceId 인덱스는 명시적으로 만들고 ObjectId는 문자열로 직렬화한다. 기존 /posts/{id}의 숫자 제약을 Mongo id에 재사용하지 않는다.
7. 이 환경은 Docker 엔진 미실행 및 로컬 SQL PDO 확장 미활성화 상태여서 외부 DB 실행 검증은 완료로 표시하지 않는다. CI에 PostgreSQL·MariaDB 테스트 행렬을 준비했다.

### 실행 명령

```powershell
# 저장소 루트, Docker 엔진이 실행 중일 때
docker compose --profile postgres up -d postgres
powershell -File tools/use_database.ps1 -App project -Driver pgsql
# MariaDB 선택 시
docker compose --profile mariadb up -d mariadb
powershell -File tools/use_database.ps1 -App project -Driver mariadb
# SQLite로 연결 원복 (다른 DB 데이터는 삭제하지 않음)
powershell -File tools/use_database.ps1 -App project -Driver sqlite
# Mongo 선택 실습: PHP ext-mongodb 설치 후
docker compose --profile mongo up -d mongo
php --ri mongodb
composer --working-dir=project require mongodb/laravel-mongodb
# project/.env.example의 MONGODB_URI/DATABASE를 .env에 반영한 뒤
php examples/mongodb/run.php
```

명령은 위에서 아래로 실행한다. `cd`는 작업 폴더 이동, `php artisan`은 Laravel 작업, `composer`는 PHP 의존성, `npm`은 Vue 자산 도구, `docker compose`는 연결 서비스를 담당한다. 주석에 별도 터미널·운영 환경·선택 실습이 지정되어 있으면 그 경계를 유지한다.

### `compose.yaml` 전체 코드

[compose.yaml](compose.yaml)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```yaml
name: laravel-study-data
services:
  postgres:
    image: postgres:17-alpine
    profiles: [postgres]
    environment:
      POSTGRES_DB: study
      POSTGRES_USER: study
      POSTGRES_PASSWORD: ${STUDY_DB_PASSWORD:-local-study-only}
    ports: ["127.0.0.1:54329:5432"]
    volumes: ["postgres-data:/var/lib/postgresql/data"]
    healthcheck:
      test: [CMD-SHELL, "pg_isready -U study -d study"]
      interval: 5s
      retries: 10
  mariadb:
    image: mariadb:11.8
    profiles: [mariadb]
    environment:
      MARIADB_DATABASE: study
      MARIADB_USER: study
      MARIADB_PASSWORD: ${STUDY_DB_PASSWORD:-local-study-only}
      MARIADB_RANDOM_ROOT_PASSWORD: "yes"
    ports: ["127.0.0.1:33069:3306"]
    volumes: ["mariadb-data:/var/lib/mysql"]
  mongo:
    image: mongo:8
    profiles: [mongo]
    environment:
      MONGO_INITDB_ROOT_USERNAME: study
      MONGO_INITDB_ROOT_PASSWORD: ${STUDY_DB_PASSWORD:-local-study-only}
    ports: ["127.0.0.1:27019:27017"]
    volumes: ["mongo-data:/data/db"]
volumes:
  postgres-data:
  mariadb-data:
  mongo-data:
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 2 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 3 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 4 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 5 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 6 | 프로세스가 사용할 환경 설정 경계를 지정한다. |
| 7 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 8 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 9 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 10 | 허용할 호스트 주소·포트와 컨테이너 포트를 연결한다. |
| 11 | 컨테이너 교체 후에도 보존할 저장 볼륨을 연결한다. |
| 12 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 13 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 14 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 15 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 16 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 17 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 18 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 19 | 프로세스가 사용할 환경 설정 경계를 지정한다. |
| 20 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 21 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 22 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 23 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 24 | 허용할 호스트 주소·포트와 컨테이너 포트를 연결한다. |
| 25 | 컨테이너 교체 후에도 보존할 저장 볼륨을 연결한다. |
| 26 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 27 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 28 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 29 | 프로세스가 사용할 환경 설정 경계를 지정한다. |
| 30 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 31 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 32 | 허용할 호스트 주소·포트와 컨테이너 포트를 연결한다. |
| 33 | 컨테이너 교체 후에도 보존할 저장 볼륨을 연결한다. |
| 34 | 컨테이너 교체 후에도 보존할 저장 볼륨을 연결한다. |
| 35 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 36 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |
| 37 | 현재 서비스·작업·단계의 구성 키와 값을 선언한다. |


### `tools/use_database.ps1` 전체 코드

[tools/use_database.ps1](tools/use_database.ps1)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```powershell
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
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 2 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 3 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 4 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 5 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 6 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 7 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 8 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 9 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 10 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 11 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 12 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 13 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 14 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 15 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 16 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 17 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 18 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 19 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 20 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 21 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 22 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 23 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 24 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 25 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 26 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 27 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 28 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 29 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 30 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 31 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 32 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 33 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 34 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 35 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 36 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 37 | 이 작업에서 사용할 경로·설정값을 계산하거나 기존 파일 내용을 읽는다. |
| 38 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 39 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 40 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 41 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 42 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 43 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 44 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 45 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 46 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |
| 47 | 명시한 애플리케이션·파일·Docker 대상에 대해 검증된 운영 절차를 실행한다. |


### `project/app/Models/Note.php` 전체 코드

[project/app/Models/Note.php](project/app/Models/Note.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Attributes\Fillable;
use Illuminate\Database\Eloquent\Builder;
use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\BelongsToMany;
use Illuminate\Database\Eloquent\Relations\HasMany;

#[Fillable(['title', 'body'])]
class Note extends Model
{
    public function comments(): HasMany
    {
        return $this->hasMany(Comment::class);
    }

    public function user(): BelongsTo
    {
        return $this->belongsTo(User::class);
    }

    public function tags(): BelongsToMany
    {
        return $this->belongsToMany(Tag::class);
    }

    public function scopeSearch(Builder $query, ?string $term): Builder
    {
        $term = trim((string) $term);
        if ($term === '') {
            return $query;
        }

        $like = '%'.$term.'%';

        return $query->where(function (Builder $inner) use ($like) {
            $inner->whereLike('title', $like)->orWhereLike('body', $like);
        });
    }

    public function scopeTagged(Builder $query, ?string $tag): Builder
    {
        $tag = trim((string) $tag);
        if ($tag === '') {
            return $query;
        }

        return $query->whereHas('tags', fn (Builder $inner) => $inner->where('name', $tag));
    }

    public function syncTagString(?string $raw): void
    {
        $this->syncTagNames(preg_split('/[,，]/u', (string) $raw) ?: []);
    }

    public function syncTagNames(array $raw): void
    {
        $names = collect($raw)
            ->map(fn ($name) => trim((string) $name))
            ->filter(fn ($name) => $name !== '')
            ->unique()
            ->take(8)
            ->map(fn ($name) => mb_substr($name, 0, 30));

        $ids = $names->map(fn (string $name) => Tag::query()->firstOrCreate(['name' => $name])->id);

        $this->tags()->sync($ids->all());
    }
}
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | PHP 코드 시작을 선언한다. |
| 2 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 3 | 이 클래스가 속한 이름 공간을 지정해 같은 이름의 충돌을 막는다. |
| 4 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 5 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 6 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 7 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 8 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 9 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 10 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 11 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 12 | PHP 속성으로 클래스의 허용 필드·이름·버전·설명을 선언한다. |
| 13 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 14 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 15 | `comments` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 16 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 17 | 현재 모델의 자식 여러 건을 찾는 관계를 정의한다. |
| 18 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 19 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 20 | `user` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 21 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 22 | 현재 모델에서 소유자나 부모 한 건을 찾는 관계를 정의한다. |
| 23 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 24 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 25 | `tags` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 26 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 27 | 현재 모델에서 소유자나 부모 한 건을 찾는 관계를 정의한다. |
| 28 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 29 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 30 | `scopeSearch` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 31 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 32 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 33 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 34 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 35 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 36 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 37 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 38 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 39 | 사용자 입력을 바인딩한 조회 조건을 추가한다. |
| 40 | DB 드라이버에 맞는 부분 일치 검색 조건을 만든다. |
| 41 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 42 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 43 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 44 | `scopeTagged` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 45 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 46 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 47 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 48 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 49 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 50 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 51 | 사용자 입력을 바인딩한 조회 조건을 추가한다. |
| 52 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 53 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 54 | `syncTagString` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 55 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 56 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 57 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 58 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 59 | `syncTagNames` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 60 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 61 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 62 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 63 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 64 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 65 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 66 | UTF-8 문자 기준으로 텍스트 길이를 제한한다. |
| 67 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 68 | 모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다. |
| 69 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 70 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 71 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 72 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `examples/mongodb/ArchiveDocument.php` 전체 코드

[examples/mongodb/ArchiveDocument.php](examples/mongodb/ArchiveDocument.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace Study\Mongo;

use MongoDB\Laravel\Eloquent\Model;

class ArchiveDocument extends Model
{
    protected $connection = 'mongodb';

    protected $table = 'archive_documents';

    protected $fillable = ['sourceId', 'text', 'tags'];
}
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | PHP 코드 시작을 선언한다. |
| 2 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 3 | 이 클래스가 속한 이름 공간을 지정해 같은 이름의 충돌을 막는다. |
| 4 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 5 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 6 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 7 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 8 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 9 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 10 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 11 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 12 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 13 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 14 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `examples/mongodb/run.php` 전체 코드

[examples/mongodb/run.php](examples/mongodb/run.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

use Illuminate\Contracts\Console\Kernel;
use Study\Mongo\ArchiveDocument;

require __DIR__.'/../../project/vendor/autoload.php';
$app = require __DIR__.'/../../project/bootstrap/app.php';
$app->make(Kernel::class)->bootstrap();
require __DIR__.'/ArchiveDocument.php';

$document = ArchiveDocument::query()->create([
    'sourceId' => 1, 'text' => 'Laravel 문서 저장 실험', 'tags' => ['study'],
]);
echo $document->getKey().PHP_EOL;
echo ArchiveDocument::query()->where('sourceId', 1)->firstOrFail()->text.PHP_EOL;
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | PHP 코드 시작을 선언한다. |
| 2 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 3 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 4 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 5 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 6 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 7 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 8 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 9 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 10 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 11 | 모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다. |
| 12 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 13 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 14 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 15 | 모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다. |


## ④ 🔗 연동 포인트

SQL DB를 바꿔도 Vue가 읽는 API 필드와 상태 코드는 유지한다. Mongo ObjectId를 공개하려면 별도 API 자원 스키마를 설계한다. 다음 단계에서는 DB 내부 변화와 무관하게 같은 Vue UI를 연동한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| could not find driver | pdo_pgsql/pdo_mysql 비활성화 | php --ini의 확장을 켜고 새 PHP 프로세스로 실행 |
| Connection refused | Docker 엔진·profile·포트가 다름 | docker compose ps와 공개 로컬 포트 확인 |
| 새 DB가 비어 있음 | 연결 전환만 하고 데이터 이전을 안 함 | 원본 보존 후 export/import와 FK·건수 검증 |

## ⑥ 직접 해보기

1. PostgreSQL 연결 뒤 같은 ContractTest를 실행하고 결과를 기록한다.
2. MariaDB에서 한글 태그를 저장·검색한다.
3. Mongo 보관 문서의 id 타입과 SQL id를 출력해 URL 설계 차이를 적는다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] PostgreSQL과 MariaDB의 연결·마이그레이션 절차를 작성했다.
- [ ] SQL 모델과 Mongo 전용 모델을 구분했다.
- [ ] 실제 DB 실행 결과를 별도로 기록한다.
- [ ] 데이터 이전·백업·원복 절차를 확인한다.

## ⑧ 다음 단계 연결

PostgreSQL·MariaDB 연결을 전환하고 MongoDB 모델의 다른 전제를 설명한다. 이 결과를 [study12.md](study12.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://laravel.com/docs/13.x/database)
- [공식 문서 2](https://www.mongodb.com/docs/drivers/php/laravel-mongodb/current/)

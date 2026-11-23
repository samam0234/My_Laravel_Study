# study0 · 환경 설정

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

PHP·Composer·Node를 확인하고 Laravel 안에 Vue를 두는 개발 환경을 재현한다.

## ② 📖 이론

Laravel은 요청을 받아 PHP로 업무 규칙을 실행하는 풀스택 프레임워크다. Artisan은 반복 작업을 대신하는 작업대, Composer는 PHP 패키지 창고다. Vue는 같은 Laravel 프로젝트의 `resources/js`에서 화면 상태를 관리한다. Vite는 개발 중 변경을 전달하고 운영용 파일을 만든다. Node는 자산 빌드 때 사용하며 별도 서비스 서버를 배포하지 않는다.

이 저장소는 `demo/`(기초 게시판)와 `project/`(심화 서재)라는 두 학습 결과를 보존한다. 한 서비스를 운영할 때는 `project/` 하나만 배포한다. 루트 `js/`, `ts/`별 실습은 제거했다. Vue SFC 내부의 스크립트와 Vite 설정은 Vue 실행에 필요한 파일이다.

| 위치·용어 | 역할 |
|---|---|
| `routes/web.php`, `routes/api.php` | 웹 주소와 JSON 주소의 접수 창구 |
| `app/Http/Controllers` | 요청을 검증하고 서비스를 호출하는 컨트롤러 |
| `app/Models`, Eloquent | DB 행과 관계를 PHP 객체로 표현 |
| `database/migrations` | DB 구조 변경의 시간순 기록 |
| `resources/views`, Blade | 서버가 그리는 HTML 템플릿 |
| `resources/js`, Vue SFC | 브라우저의 화면·입력·비동기 상태 |
| `public` | 웹 서버가 외부에 공개하는 유일한 루트 |
| `storage/app/private` | 업로드·설정을 보관하는 비공개 디스크 |
| `.env`, `config` | 설치별 비밀값과 애플리케이션 설정 |
| `vendor`, `node_modules` | 잠금 파일로 재설치하는 의존성 |
| Service Container, Middleware, Policy | 의존성 제공, 요청 통과 규칙, 자원 권한 규칙 |

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. Windows에 PHP 8.4와 Composer 2, Node 24를 설치한다. `php --ini`로 실제 설정 파일을 찾고 `mbstring`, `openssl`, `fileinfo`, `pdo_sqlite`를 확인한다. SQL 서버 실습은 `pdo_pgsql` 또는 `pdo_mysql`도 필요하다.
2. 아래의 **새 프로젝트 명령은 빈 연습 폴더에서만** 사용한다. 현재 저장소의 `demo` 위에 다시 생성하지 않는다. 재현 실행은 README의 `composer install`부터 시작한다.
3. `.env.example`을 `.env`로 복사하고 `key:generate`를 한 번 실행한다. `.env`의 키·비밀번호는 커밋하지 않는다. 기존 `.env`가 있으면 먼저 내용을 보존한다.
4. SQLite 파일을 만든 뒤 마이그레이션한다. 시드는 로컬에서만 실행한다. `npm ci`는 커밋된 `package-lock.json`의 정확한 의존성을 설치한다.
5. 터미널 A는 PHP 서버, B는 `npm run dev`를 실행한다. 브라우저는 PHP 주소 `/app`을 연다. 운영은 `npm run build` 결과를 Laravel과 함께 제공한다.
6. VS Code 확장은 Laravel 공식 확장, PHP Intelephense, Vue - Official을 사용한다. 동일 기능의 PHP 언어 서버를 여러 개 켰다면 중복 진단을 점검한다.
7. `git init`, `.gitignore`, 첫 커밋으로 변경 이력을 시작한다. 이 저장소에는 이미 Git이 있으므로 다시 초기화할 필요가 없다.

### 실행 명령

```powershell
# 새 빈 연습 폴더에서 생성할 때
php -v
composer -V
node -v
composer create-project laravel/laravel sandbox "^13.0"
cd sandbox
git init
Copy-Item .env.example .env
php artisan key:generate
php artisan about
php artisan serve
# 이 저장소를 실행할 때는 README의 composer install, npm ci를 사용한다.
```

명령은 위에서 아래로 실행한다. `cd`는 작업 폴더 이동, `php artisan`은 Laravel 작업, `composer`는 PHP 의존성, `npm`은 Vue 자산 도구, `docker compose`는 연결 서비스를 담당한다. 주석에 별도 터미널·운영 환경·선택 실습이 지정되어 있으면 그 경계를 유지한다.

### `demo/composer.json` 전체 코드

[demo/composer.json](demo/composer.json)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```json
{
    "$schema": "https://getcomposer.org/schema.json",
    "name": "laravel/laravel",
    "type": "project",
    "description": "The skeleton application for the Laravel framework.",
    "keywords": ["laravel", "framework"],
    "license": "MIT",
    "require": {
        "php": "^8.3",
        "laravel/framework": "^13.17",
        "laravel/sanctum": "^4.3",
        "laravel/tinker": "^3.0"
    },
    "require-dev": {
        "fakerphp/faker": "^1.23",
        "laravel/boost": "^2.10",
        "laravel/pail": "^1.2.5",
        "laravel/pao": "^1.0.6",
        "laravel/pint": "^1.27",
        "mockery/mockery": "^1.6",
        "nunomaduro/collision": "^8.6",
        "phpunit/phpunit": "^12.5.12"
    },
    "autoload": {
        "psr-4": {
            "App\\": "app/",
            "Database\\Factories\\": "database/factories/",
            "Database\\Seeders\\": "database/seeders/"
        }
    },
    "autoload-dev": {
        "psr-4": {
            "Tests\\": "tests/"
        }
    },
    "scripts": {
        "setup": [
            "composer install",
            "@php -r \"file_exists('.env') || copy('.env.example', '.env');\"",
            "@php artisan key:generate",
            "@php artisan migrate --force",
            "npm install --ignore-scripts",
            "npm run build"
        ],
        "dev": [
            "Composer\\Config::disableProcessTimeout",
            "@php artisan dev"
        ],
        "test": [
            "@php artisan config:clear --ansi @no_additional_args",
            "@php artisan test"
        ],
        "post-autoload-dump": [
            "Illuminate\\Foundation\\ComposerScripts::postAutoloadDump",
            "@php artisan package:discover --ansi"
        ],
        "post-update-cmd": [
            "@php artisan vendor:publish --tag=laravel-assets --ansi --force"
        ],
        "post-root-package-install": [
            "@php -r \"file_exists('.env') || copy('.env.example', '.env');\""
        ],
        "post-create-project-cmd": [
            "@php artisan key:generate --ansi",
            "@php -r \"file_exists('database/database.sqlite') || touch('database/database.sqlite');\"",
            "@php artisan migrate --graceful --ansi"
        ],
        "pre-package-uninstall": [
            "Illuminate\\Foundation\\ComposerScripts::prePackageUninstall"
        ]
    },
    "extra": {
        "laravel": {
            "dont-discover": []
        }
    },
    "config": {
        "optimize-autoloader": true,
        "preferred-install": "dist",
        "sort-packages": true,
        "allow-plugins": {
            "pestphp/pest-plugin": true,
            "php-http/discovery": true
        }
    },
    "minimum-stability": "stable",
    "prefer-stable": true
}
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 2 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 3 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 4 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 5 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 6 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 7 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 8 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 9 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 10 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 11 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 12 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 13 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 14 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 15 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 16 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 17 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 18 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 19 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 20 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 21 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 22 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 23 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 24 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 25 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 26 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 27 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 28 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 29 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 30 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 31 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 32 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 33 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 34 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 35 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 36 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 37 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 38 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 39 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 40 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 41 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 42 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 43 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 44 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 45 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 46 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 47 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 48 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 49 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 50 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 51 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 52 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 53 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 54 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 55 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 56 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 57 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 58 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 59 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 60 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 61 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 62 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 63 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 64 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 65 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 66 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 67 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 68 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 69 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 70 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 71 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 72 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 73 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 74 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 75 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 76 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 77 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 78 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 79 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 80 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 81 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 82 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 83 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 84 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 85 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 86 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 87 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 88 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `demo/.env.example` 전체 코드

[demo/.env.example](demo/.env.example)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```dotenv
APP_NAME=LaravelStudy
APP_ENV=local
APP_KEY=
APP_DEBUG=true
APP_URL=http://127.0.0.1:8000

APP_LOCALE=ko
APP_FALLBACK_LOCALE=en
APP_FAKER_LOCALE=ko_KR

APP_MAINTENANCE_DRIVER=file
# APP_MAINTENANCE_STORE=database

# PHP_CLI_SERVER_WORKERS=4

BCRYPT_ROUNDS=12

LOG_CHANNEL=stack
LOG_STACK=single
LOG_DEPRECATIONS_CHANNEL=null
LOG_LEVEL=debug

DB_CONNECTION=sqlite
# DB_HOST=127.0.0.1
# DB_PORT=3306
# DB_DATABASE=laravel
# DB_USERNAME=root
# DB_PASSWORD=

SESSION_DRIVER=database
SESSION_LIFETIME=120
SESSION_ENCRYPT=false
SESSION_PATH=/
SESSION_DOMAIN=null

BROADCAST_CONNECTION=log
FILESYSTEM_DISK=local
QUEUE_CONNECTION=database

CACHE_STORE=database
# CACHE_PREFIX=

MEMCACHED_HOST=127.0.0.1

REDIS_CLIENT=phpredis
REDIS_HOST=127.0.0.1
REDIS_PASSWORD=null
REDIS_PORT=6379

MAIL_MAILER=log
MAIL_SCHEME=null
MAIL_HOST=127.0.0.1
MAIL_PORT=2525
MAIL_USERNAME=null
MAIL_PASSWORD=null
MAIL_FROM_ADDRESS="hello@example.com"
MAIL_FROM_NAME="${APP_NAME}"

AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
AWS_DEFAULT_REGION=us-east-1
AWS_BUCKET=
AWS_USE_PATH_STYLE_ENDPOINT=false

VITE_APP_NAME="${APP_NAME}"

CORS_ORIGIN=http://127.0.0.1:5173
AI_DRIVER=mock
AI_URL=http://127.0.0.1:11434
AI_MODEL=gemma4:12b
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 2 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 3 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 4 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 5 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 6 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 7 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 8 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 9 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 10 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 11 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 12 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 13 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 14 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 15 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 16 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 17 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 18 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 19 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 20 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 21 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 22 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 23 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 24 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 25 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 26 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 27 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 28 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 29 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 30 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 31 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 32 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 33 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 34 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 35 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 36 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 37 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 38 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 39 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 40 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 41 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 42 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 43 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 44 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 45 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 46 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 47 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 48 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 49 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 50 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 51 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 52 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 53 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 54 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 55 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 56 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 57 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 58 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 59 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 60 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 61 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 62 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 63 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 64 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 65 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 66 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 67 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 68 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 69 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |
| 70 | 설치 환경별 설정값을 지정한다. 값 변경 뒤 설정 캐시·프로세스를 갱신한다. |


### `.gitignore` 전체 코드

[.gitignore](.gitignore)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```text
.DS_Store
Thumbs.db
*.log
node_modules/
dist/
.env
.env.production
__pycache__/
backups/
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 2 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 3 | 다음 동작·형식·설정의 의미를 설명하는 주석이다. |
| 4 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 5 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 6 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 7 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 8 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 9 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |


### `demo/vite.config.js` 전체 코드

[demo/vite.config.js](demo/vite.config.js)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```javascript
import { defineConfig } from 'vite';
import laravel from 'laravel-vite-plugin';
import vue from '@vitejs/plugin-vue';
export default defineConfig({
    plugins: [laravel({ input: ['resources/js/app.js', 'resources/js/docs.js'], refresh: true }), vue()],
});
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 2 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 3 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 4 | 현재 모듈이 사용할 값 또는 외부에 제공할 인터페이스를 선언한다. |
| 5 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 6 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


## ④ 🔗 연동 포인트

Git은 소스와 잠금 파일을 보관하고 `.env`·DB·생성 파일은 제외한다. 다음 단계는 같은 PHP 서버의 `/`를 통해 응답을 확인한다. API·메일·AI 키는 서버 환경변수로만 읽으며 `VITE_` 변수는 브라우저에 공개된다는 경계를 유지한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| php가 인식되지 않음 | 설치 경로가 PATH에 없음 | PHP 경로를 PATH에 추가하고 새 터미널에서 php -v 확인 |
| could not find driver | 현재 CLI php.ini에 PDO 확장 미설정 | php --ini, php -m 확인 후 필요한 확장을 활성화 |
| No application encryption key | 새 .env에 APP_KEY가 비어 있음 | php artisan key:generate 실행; 기존 운영 키는 재생성하지 않음 |

## ⑥ 직접 해보기

1. php artisan about의 버전을 잠금 파일과 대조한다.
2. 민감하지 않은 APP_NAME을 변경하고 config:clear 후 화면에 반영한다.
3. git check-ignore .env가 .env를 제외하는지 앱 폴더에서 확인한다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] Laravel 프로젝트 (composer create-project)
- [ ] 버전 명령과 필수 확장을 확인했다.
- [ ] .env와 .gitignore의 역할을 설명할 수 있다.
- [ ] 개발 서버와 Vite를 서로 다른 터미널에서 실행했다.

## ⑧ 다음 단계 연결

PHP·Composer·Node를 확인하고 Laravel 안에 Vue를 두는 개발 환경을 재현한다. 이 결과를 [study1.md](study1.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://laravel.com/docs/13.x/installation)
- [공식 문서 2](https://vuejs.org/guide/quick-start.html)

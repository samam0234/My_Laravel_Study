# study1. 만드는 방법 및 명령어, 실습1

study0의 지도를 실제 폴더로 만듭니다. Laravel 앱은 `demo/`에 두고, 나중 화면용 JavaScript와 TypeScript는 `js/`, `ts/`에서 따로 실행합니다.

이번 실습의 끝 상태는 주소 `/`에 Blade 환영 화면이 나오고, `/up`이 200을 주는 것입니다.

## 1. 개발 환경

이 저장소를 확인한 환경은 아래와 같습니다.

| 도구 | 버전 |
|---|---|
| PHP | 8.4.25 (winget `PHP.PHP.8.4`, ZTS) |
| Composer | 2.10.3 |
| Laravel | Framework 13.38.0, 스켈레톤 `laravel/laravel` v13.11.0 |
| Node.js | 24.14.0 (study10의 JS/TS 화면에서 사용) |

Windows에는 PHP가 기본으로 없습니다.

```powershell
winget install --id PHP.PHP.8.4 -e
php -v
```

설치 직후 터미널이 `php`를 못 찾으면 터미널을 다시 엽니다. winget 빌드는 `php.ini` 없이 `php.ini-development`만 둡니다. Laravel과 Composer는 `openssl`, `mbstring`, `fileinfo`, `curl`, `pdo_sqlite`, `sqlite3`, `zip`이 필요합니다. `php.ini-development`를 `php.ini`로 복사한 뒤 `extension_dir = "ext"`와 위 확장을 켜고, `date.timezone = Asia/Seoul`을 적습니다.

Composer는 winget에 패키지가 없어서 공식 설치 스크립트로 받았습니다.

```powershell
php -r "copy('https://getcomposer.org/installer', 'composer-setup.php');"
php composer-setup.php --install-dir="$env:LOCALAPPDATA\Composer" --filename=composer.phar
php -r "unlink('composer-setup.php');"
composer -V
```

`php.ini`를 만들기 전에 Composer를 돌리면 `openssl` 확장이 없다는 오류가 납니다. 확장을 켠 뒤에 설치합니다.

## 2. 프로젝트 생성 명령어

저장소 루트에서 `demo` 폴더로 앱을 만들었습니다. SQLite가 기본입니다. Node 의존성은 아직 설치하지 않습니다. 화면 CSS는 `public/css/app.css`에 두어, Vite 없이 Blade만으로 확인하게 했습니다. `package.json`과 `vite.config.js`는 스켈레톤 그대로 남아 있습니다.

```powershell
composer create-project laravel/laravel demo --no-interaction
```

생성 직후 Composer가 `.env`를 복사하고, `APP_KEY`를 만들고, `database/database.sqlite`를 만든 다음 기본 마이그레이션을 실행합니다. 사용자, 세션, 캐시, 잡 테이블이 생깁니다.

`composer create-project`가 `demo/.git`을 만들면 지웁니다. 이 저장소의 Git 루트는 Laravel 폴더입니다.

자주 여는 파일은 세 개입니다.

- `composer.json`: PHP `^8.3`, `laravel/framework` `^13.17`
- `bootstrap/app.php`: 웹 라우트와 `/up` 헬스 체크를 등록
- `routes/web.php`: URL과 컨트롤러를 연결

`.env`, SQLite 파일, `vendor/`는 Git에 올리지 않습니다. 클론한 뒤에는 `demo/`에서 아래를 실행합니다.

```powershell
composer install
copy .env.example .env
php artisan key:generate
php artisan migrate
```

## 3. 자주 쓰는 명령어

모두 `demo/` 안에서 실행합니다.

```powershell
php artisan serve --host=127.0.0.1 --port=8000
php artisan route:list
php artisan test
php artisan migrate
php artisan tinker
php artisan make:model Post -mcr
```

`make:model`의 `-m`은 마이그레이션, `-c`는 컨트롤러, `-r`은 리소스 액션입니다. study2와 study3에서 이 생성기 결과를 손으로 읽습니다. 서버를 끈 뒤 개발 DB를 비우고 싶으면 `php artisan migrate:fresh`를 씁니다. 개발용 데이터가 사라집니다.

Laravel 13의 `route:list`에는 `--columns` 옵션이 없습니다. 컬럼을 고르려면 `--columns` 대신 그대로 `php artisan route:list`를 실행합니다.

## 4. 설정에서 먼저 바꾼 것

`config/app.php`의 시간대를 서울로 고정했습니다. 로캘은 `.env`가 읽습니다.

```php
'timezone' => 'Asia/Seoul',
```

`.env.example`은 다음 값입니다. 실제 `.env`도 같게 맞추되 `APP_KEY`는 생성기가 만든 값을 유지합니다.

```
APP_NAME=LaravelStudy
APP_URL=http://127.0.0.1:8000
APP_LOCALE=ko
APP_FALLBACK_LOCALE=en
APP_FAKER_LOCALE=ko_KR
```

번역 파일이 없는 키는 영어 또는 키 이름 그대로 떨어집니다. 화면 문장은 Blade에 한국어로 적습니다. Django의 `TIME_ZONE`, `LANGUAGE_CODE`와 같은 자리입니다.

`php artisan tinker --execute`로 확인한 값은 `Asia/Seoul ko LaravelStudy`입니다.

## 5. 실습1: 첫 화면

라우트 한 줄이 컨트롤러 액션을 고릅니다. 헬스 체크 `/up`은 `bootstrap/app.php`의 `health: '/up'`이 이미 등록합니다.

```php
Route::get('/', [HomeController::class, 'index'])->name('home');
```

```php
class HomeController extends Controller
{
    public function index()
    {
        return view('home');
    }
}
```

`view('home')`은 `resources/views/home.blade.php`를 찾습니다. 레이아웃은 `layouts/app.blade.php`이고, 스타일은 `public/css/app.css`입니다. `{{ }}`는 이스케이프된 출력입니다.

스켈레톤의 `resources/views/welcome.blade.php`와 `tests/Feature/ExampleTest.php`는 이 라우트로 바꿔 제거했습니다.

## 6. 검증

`demo/`에서 `php artisan test --filter=HomeTest` 결과입니다.

```
PASS  Tests\Feature\HomeTest
✓ home renders the blade intro
✓ health check is ok

Tests: 2 passed (4 assertions)
```

서버를 띄운 뒤 HTTP로 확인했습니다.

```powershell
php artisan serve --host=127.0.0.1 --port=8000
```

| 주소 | 결과 |
|---|---|
| `GET /` | 200. 본문에 "Laravel 게시판을 이 폴더에서 만듭니다." |
| `GET /up` | 200. 제목이 `LaravelStudy`, 본문에 Application up |
| `GET /css/app.css` | 200 |

`php artisan route:list`에는 `GET /` 이름 `home`, 액션 `HomeController@index`가 보입니다. `/up`은 프레임워크 헬스 라우트라 이 목록의 앱 라우트 한 줄과는 따로 등록되어 있고, 테스트와 HTTP 모두 200입니다.

브라우저 자동화 도구는 이 환경에 연결되지 않았습니다. 화면 확인은 Feature 테스트와 HTTP 응답으로 했습니다.

다음 문서는 [study2.md](study2.md)입니다. `posts` 테이블과 `Post` 모델을 만듭니다.

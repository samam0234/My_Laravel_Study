# study4 · 라우팅과 요청 처리

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

정적·동적 URL, 쿼리, 응답과 오류 경로를 하나의 흐름으로 추적한다.

## ② 📖 이론

라우터는 URL과 메서드의 조합을 액션으로 바꾼다. 같은 `/posts`라도 GET은 목록, POST는 등록이다. `/posts/{post}`는 경로 값, `?q=Laravel&page=2`는 조회 조건이다. Blade의 named route는 URL이 바뀌어도 이름으로 이동하게 하는 주소록이다.

모델 바인딩은 id를 모델로 찾고 없으면 404를 만든다. `/posts/create`를 동적 경로보다 먼저 등록해야 create가 id로 해석되지 않는다. 웹 요청은 리다이렉트와 HTML, API는 JSON과 상태 코드를 응답한다. 표준 API에서 숫자가 아닌 id는 400, 없는 숫자 id는 404다. bootstrap의 예외 응답 변환은 `/api`에만 적용하고 이전 `/api/v1` 동작은 유지한다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. `route:list --path=api`로 주소·메서드·인증 미들웨어를 확인한다.
2. `/posts`, `/posts/999999`, `/api/posts?q=Laravel&limit=1`, `/api/posts/not-a-number`를 요청한다.
3. 폼 action의 route 이름과 web.php 이름을 비교한다. Vue의 fetch는 상대 주소 `/api/posts`를 쓰므로 프론트·백엔드 경로가 한 서버에서 만난다.
4. 없는 웹 주소의 HTML 404와 없는 API 주소의 `error.code=NOT_FOUND`를 대조한다. 오류마다 requestId를 헤더와 로그에서 찾는다.

### 실행 명령

```powershell
cd demo
php artisan route:list --path=api
curl.exe -i "http://127.0.0.1:8000/api/posts?q=Laravel&limit=1"
curl.exe -i http://127.0.0.1:8000/api/posts/not-a-number
```

명령은 위에서 아래로 실행한다. `cd`는 작업 폴더 이동, `php artisan`은 Laravel 작업, `composer`는 PHP 의존성, `npm`은 Vue 자산 도구, `docker compose`는 연결 서비스를 담당한다. 주석에 별도 터미널·운영 환경·선택 실습이 지정되어 있으면 그 경계를 유지한다.

### `demo/routes/web.php` 전체 코드

[demo/routes/web.php](demo/routes/web.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

use App\Http\Controllers\Auth\RegisteredUserController;
use App\Http\Controllers\Auth\SessionController;
use App\Http\Controllers\CommentController;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\LearningController;
use App\Http\Controllers\PostController;
use Illuminate\Support\Facades\Route;

Route::get('/', [HomeController::class, 'index'])->name('home');

Route::middleware('guest')->group(function () {
    Route::get('/register', [RegisteredUserController::class, 'create'])->name('register');
    Route::post('/register', [RegisteredUserController::class, 'store']);
    Route::get('/login', [SessionController::class, 'create'])->name('login');
    Route::post('/login', [SessionController::class, 'store'])->middleware('throttle:10,1');
});

Route::post('/logout', [SessionController::class, 'destroy'])
    ->middleware('auth')
    ->name('logout');

Route::middleware('auth')->group(function () {
    Route::resource('posts', PostController::class)->except(['index', 'show']);
    Route::post('/posts/{post}/comments', [CommentController::class, 'store'])
        ->name('posts.comments.store');
    Route::delete('/posts/{post}/comments/{comment}', [CommentController::class, 'destroy'])
        ->scopeBindings()
        ->name('posts.comments.destroy');
});

Route::resource('posts', PostController::class)->only(['index', 'show']);

Route::view('/app', 'workspace')->name('workspace');
Route::get('/health', fn () => response()->json(['status' => 'ok']));

Route::view('/api-docs', 'api-docs');
Route::get('/study/preferences', [LearningController::class, 'preferences'])->middleware('auth')->name('study.preferences');
Route::post('/study/preferences', [LearningController::class, 'save'])->middleware('auth')->name('study.preferences.save');
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | PHP 코드 시작을 선언한다. |
| 2 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 3 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 4 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 5 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 6 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 7 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 8 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 9 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 10 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 11 | HTTP `GET`의 `/` 주소에 동작·제약을 등록한다. |
| 12 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 13 | HTTP `MIDDLEWARE`의 `guest` 주소에 동작·제약을 등록한다. |
| 14 | HTTP `GET`의 `/register` 주소에 동작·제약을 등록한다. |
| 15 | HTTP `POST`의 `/register` 주소에 동작·제약을 등록한다. |
| 16 | HTTP `GET`의 `/login` 주소에 동작·제약을 등록한다. |
| 17 | HTTP `POST`의 `/login` 주소에 동작·제약을 등록한다. |
| 18 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 19 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 20 | HTTP `POST`의 `/logout` 주소에 동작·제약을 등록한다. |
| 21 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 22 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 23 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 24 | HTTP `MIDDLEWARE`의 `auth` 주소에 동작·제약을 등록한다. |
| 25 | HTTP `RESOURCE`의 `posts` 주소에 동작·제약을 등록한다. |
| 26 | HTTP `POST`의 `/posts/{post}/comments` 주소에 동작·제약을 등록한다. |
| 27 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 28 | HTTP `DELETE`의 `/posts/{post}/comments/{comment}` 주소에 동작·제약을 등록한다. |
| 29 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 30 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 31 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 32 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 33 | HTTP `RESOURCE`의 `posts` 주소에 동작·제약을 등록한다. |
| 34 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 35 | HTTP `VIEW`의 `/app` 주소에 동작·제약을 등록한다. |
| 36 | HTTP `GET`의 `/health` 주소에 동작·제약을 등록한다. |
| 37 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 38 | HTTP `VIEW`의 `/api-docs` 주소에 동작·제약을 등록한다. |
| 39 | HTTP `GET`의 `/study/preferences` 주소에 동작·제약을 등록한다. |
| 40 | HTTP `POST`의 `/study/preferences` 주소에 동작·제약을 등록한다. |


### `demo/routes/api.php` 전체 코드

[demo/routes/api.php](demo/routes/api.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

use App\Http\Controllers\Api\V1\CommentController;
use App\Http\Controllers\Api\V1\PostController;
use App\Http\Controllers\Api\V1\TokenController;
use Illuminate\Support\Facades\Route;

Route::prefix('v1')->group(function () {
    Route::post('/login', [TokenController::class, 'store']);

    Route::get('/posts', [PostController::class, 'index']);
    Route::get('/posts/{post}', [PostController::class, 'show']);
    Route::get('/posts/{post}/comments', [CommentController::class, 'index']);

    Route::middleware('auth:sanctum')->group(function () {
        Route::post('/logout', [TokenController::class, 'destroy']);
        Route::post('/posts', [PostController::class, 'store']);
        Route::match(['put', 'patch'], '/posts/{post}', [PostController::class, 'update']);
        Route::delete('/posts/{post}', [PostController::class, 'destroy']);
        Route::post('/posts/{post}/comments', [CommentController::class, 'store']);
        Route::delete('/posts/{post}/comments/{comment}', [CommentController::class, 'destroy'])
            ->scopeBindings();
    });
});

use App\Http\Controllers\Api\AuthController as ContractAuth;
use App\Http\Controllers\Api\CommentContractController;
use App\Http\Controllers\Api\ContractController;
use App\Services\LibraryStats;

Route::get('/posts/{post}/comments', [CommentContractController::class, 'index'])->whereNumber('post');
Route::post('/posts/{post}/comments', [CommentContractController::class, 'store'])->middleware('auth:sanctum')->whereNumber('post');
Route::delete('/comments/{comment}', [CommentContractController::class, 'destroy'])->middleware('auth:sanctum')->whereNumber('comment');
Route::post('/auth/signup', [ContractAuth::class, 'signup'])->middleware('throttle:10,1');
Route::post('/auth/login', [ContractAuth::class, 'login'])->middleware('throttle:10,1');
Route::get('/posts', [ContractController::class, 'index']);
Route::get('/posts/{id}', [ContractController::class, 'show'])->whereNumber('id');
Route::middleware('auth:sanctum')->group(function () {
    Route::get('/auth/me', [ContractAuth::class, 'me']);
    Route::post('/auth/logout', [ContractAuth::class, 'logout']);
    Route::post('/posts', [ContractController::class, 'store']);
    Route::patch('/posts/{id}', [ContractController::class, 'update'])->whereNumber('id');
    Route::delete('/posts/{id}', [ContractController::class, 'destroy'])->whereNumber('id');
});

Route::get('/posts/{invalid}', fn () => abort(400))->where('invalid', '[^0-9/]+');

Route::get('/stats', fn (LibraryStats $stats) => response()->json(['data' => ['total' => $stats->total()]]));
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | PHP 코드 시작을 선언한다. |
| 2 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 3 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 4 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 5 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 6 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 7 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 8 | HTTP `PREFIX`의 `v1` 주소에 동작·제약을 등록한다. |
| 9 | HTTP `POST`의 `/login` 주소에 동작·제약을 등록한다. |
| 10 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 11 | HTTP `GET`의 `/posts` 주소에 동작·제약을 등록한다. |
| 12 | HTTP `GET`의 `/posts/{post}` 주소에 동작·제약을 등록한다. |
| 13 | HTTP `GET`의 `/posts/{post}/comments` 주소에 동작·제약을 등록한다. |
| 14 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 15 | HTTP `MIDDLEWARE`의 `auth:sanctum` 주소에 동작·제약을 등록한다. |
| 16 | HTTP `POST`의 `/logout` 주소에 동작·제약을 등록한다. |
| 17 | HTTP `POST`의 `/posts` 주소에 동작·제약을 등록한다. |
| 18 | 라우트 그룹·인증 미들웨어·자원 경로를 묶어서 등록한다. |
| 19 | HTTP `DELETE`의 `/posts/{post}` 주소에 동작·제약을 등록한다. |
| 20 | HTTP `POST`의 `/posts/{post}/comments` 주소에 동작·제약을 등록한다. |
| 21 | HTTP `DELETE`의 `/posts/{post}/comments/{comment}` 주소에 동작·제약을 등록한다. |
| 22 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 23 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 24 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 25 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 26 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 27 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 28 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 29 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 30 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 31 | HTTP `GET`의 `/posts/{post}/comments` 주소에 동작·제약을 등록한다. |
| 32 | HTTP `POST`의 `/posts/{post}/comments` 주소에 동작·제약을 등록한다. |
| 33 | HTTP `DELETE`의 `/comments/{comment}` 주소에 동작·제약을 등록한다. |
| 34 | HTTP `POST`의 `/auth/signup` 주소에 동작·제약을 등록한다. |
| 35 | HTTP `POST`의 `/auth/login` 주소에 동작·제약을 등록한다. |
| 36 | HTTP `GET`의 `/posts` 주소에 동작·제약을 등록한다. |
| 37 | HTTP `GET`의 `/posts/{id}` 주소에 동작·제약을 등록한다. |
| 38 | HTTP `MIDDLEWARE`의 `auth:sanctum` 주소에 동작·제약을 등록한다. |
| 39 | HTTP `GET`의 `/auth/me` 주소에 동작·제약을 등록한다. |
| 40 | HTTP `POST`의 `/auth/logout` 주소에 동작·제약을 등록한다. |
| 41 | HTTP `POST`의 `/posts` 주소에 동작·제약을 등록한다. |
| 42 | HTTP `PATCH`의 `/posts/{id}` 주소에 동작·제약을 등록한다. |
| 43 | HTTP `DELETE`의 `/posts/{id}` 주소에 동작·제약을 등록한다. |
| 44 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 45 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 46 | HTTP `GET`의 `/posts/{invalid}` 주소에 동작·제약을 등록한다. |
| 47 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 48 | HTTP `GET`의 `/stats` 주소에 동작·제약을 등록한다. |


### `demo/bootstrap/app.php` 전체 코드

[demo/bootstrap/app.php](demo/bootstrap/app.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

use App\Http\Middleware\RequestContext;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Http\Request;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\Response;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        $middleware->prepend(RequestContext::class);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->shouldRenderJsonWhen(fn (Request $request) => $request->is('api/*') || $request->expectsJson());
        $exceptions->respond(function (Response $response): Response {
            $request = request();
            if (! $request->is('api/*') || $request->is('api/v1/*') || $response->getStatusCode() < 400) {
                return $response;
            }
            $status = $response->getStatusCode();
            $payload = json_decode($response->getContent(), true) ?? [];
            $fields = $payload['errors'] ?? (object) [];
            $message = $payload['message'] ?? '';
            $code = match ($status) {
                422 => 'VALIDATION_ERROR', 400 => 'BAD_REQUEST',
                401 => $message === 'INVALID_CREDENTIALS' ? 'INVALID_CREDENTIALS' : 'UNAUTHORIZED',
                403 => 'FORBIDDEN', 404 => 'NOT_FOUND', 409 => 'EMAIL_TAKEN',
                413 => 'PAYLOAD_TOO_LARGE', 429 => 'RATE_LIMITED',
                502 => 'UPSTREAM_ERROR', 503 => 'SERVICE_UNAVAILABLE', default => 'INTERNAL',
            };
            $status = $status === 422 ? 400 : $status;
            $id = $request->attributes->get('requestId', (string) Str::uuid());
            $result = response()->json(['error' => [
                'code' => $code, 'message' => $status >= 500 ? '서비스 연결을 확인해 주세요.' : '요청을 확인해 주세요.',
                'fields' => $fields, 'requestId' => $id,
            ]], $status)->header('X-Request-Id', $id)->header('Content-Type', 'application/json; charset=utf-8');
            foreach (['Retry-After', 'WWW-Authenticate', 'Allow'] as $header) {
                if ($response->headers->has($header)) {
                    $result->headers->set($header, $response->headers->get($header));
                }
            }

            return $result;
        });
    })->create();
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | PHP 코드 시작을 선언한다. |
| 2 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 3 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 4 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 5 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 6 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 7 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 8 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 9 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 10 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 11 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 12 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 13 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 14 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 15 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 16 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 17 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 18 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 19 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 20 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 21 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 22 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 23 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 24 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 25 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 26 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 27 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 28 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 29 | JSON 문자열을 구조화한 값으로 바꾸고 잘못된 입력을 처리한다. |
| 30 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 31 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 32 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 33 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 34 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 35 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 36 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 37 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 38 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 39 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 40 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 41 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 42 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 43 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 44 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 45 | 목록·청크·응답 스트림의 각 항목을 순서대로 처리한다. |
| 46 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 47 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 48 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 49 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 50 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 51 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 52 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 53 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |


## ④ 🔗 연동 포인트

URL 쿼리 → Request → 검색 scope → 페이지 JSON → Vue 목록으로 이어진다. 다음 단계에서는 GET 조회와 POST/PATCH 입력을 분리하고 실패 응답을 폼 오류로 돌려준다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| create가 404 | 동적 경로가 정적 경로보다 먼저 매칭 | 인증 resource 생성 경로를 먼저 등록 |
| 405 Method Not Allowed | URL은 맞지만 HTTP 메서드가 다름 | Network의 method와 route:list를 대조 |
| API 대신 HTML이 옴 | 주소 또는 Accept 헤더가 잘못됨 | /api 경로와 Accept application/json 확인 |

## ⑥ 직접 해보기

1. q와 page를 함께 바꾸고 화면·응답 meta를 추적한다.
2. 등록 폼 action의 route 이름을 찾아 해당 POST 라우트를 확인한다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] 동적 경로와 쿼리 파라미터를 구분했다.
- [ ] 400·404·405의 발생 조건을 재현했다.
- [ ] 웹·API 경로와 프론트 요청 주소를 맞췄다.

## ⑧ 다음 단계 연결

정적·동적 URL, 쿼리, 응답과 오류 경로를 하나의 흐름으로 추적한다. 이 결과를 [study5.md](study5.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://laravel.com/docs/13.x/routing)

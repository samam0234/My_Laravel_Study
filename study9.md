# study9. 고급 기술 구현 4 — Sanctum 토큰 인증

웹 화면은 세션 쿠키를 그대로 씁니다. `js/`와 `ts/`처럼 다른 주소에서 오는 클라이언트는 쿠키 대신 Bearer 토큰을 씁니다. 그 토큰 발급이 Sanctum입니다.

## 1. 설치

Laravel 13.38에는 Sanctum이 기본 포함되어 있지 않습니다. 맞는 버전은 4.3입니다.

```powershell
composer require laravel/sanctum
php artisan vendor:publish --provider="Laravel\Sanctum\SanctumServiceProvider"
php artisan migrate
```

이 환경에서는 `laravel/sanctum` v4.3.3이 설치됐습니다. `composer.json`의 제약은 `^4.3`입니다.

PowerShell에서 `composer require laravel/sanctum:^4.0`이라고 치면 `^`가 이스케이프되어 정확히 `4.0.0`만 요구합니다. 4.0.0은 Laravel 11의 `illuminate/console`만 받아서 설치가 실패합니다. 버전을 적을 때는 따옴표로 감싸거나, 버전 없이 `composer require laravel/sanctum`을 실행합니다.

발행 결과는 두 가지입니다.

- `config/sanctum.php`
- `database/migrations/2026_10_21_135334_create_personal_access_tokens_table.php`

`User`에 `HasApiTokens`를 붙입니다. `createToken('api')->plainTextToken`이 평문 토큰을 한 번 돌려주고, 데이터베이스에는 해시만 남습니다. 평문을 다시 조회하는 방법은 없습니다.

## 2. 로그인과 쓰기 라우트

`POST /api/v1/login`은 세션을 만들지 않습니다. 이메일과 비밀번호가 맞으면 JSON으로 토큰을 줍니다.

```php
return response()->json([
    'token' => $user->createToken('api')->plainTextToken,
    'token_type' => 'Bearer',
    'name' => $user->name,
]);
```

쓰기 라우트는 `auth:sanctum` 안에 있습니다.

| 메서드 | 주소 | 성공 코드 |
|---|---|---|
| POST | /api/v1/logout | 204. 이번 토큰만 삭제 |
| POST | /api/v1/posts | 201 |
| PUT/PATCH | /api/v1/posts/{post} | 200 |
| DELETE | /api/v1/posts/{post} | 204 |
| POST | /api/v1/posts/{post}/comments | 201 |
| DELETE | /api/v1/posts/{post}/comments/{comment} | 204 |

글 작성은 웹과 같이 `$request->user()->posts()->create()`입니다. 수정과 삭제는 study5의 `PostPolicy`, 댓글 삭제는 `CommentPolicy`를 그대로 부릅니다. 다른 사용자의 토큰으로 고치면 403입니다. 토큰이 없거나 로그아웃으로 지운 토큰이면 401입니다.

헤더는 `Authorization: Bearer <토큰>`입니다.

## 3. 테스트에서 가드가 남는 문제

한 테스트 메서드 안에서 토큰을 바꿔 여러 번 호출하면, 같은 애플리케이션 인스턴스의 가드가 이전 사용자를 기억할 수 있습니다. 두 번째 토큰이 무시되고 작성자 수정이 403 대신 200이 됐습니다. 요청 사이에 `$this->app['auth']->forgetGuards()`를 호출하면 다음 요청이 헤더의 토큰을 다시 읽습니다. `php artisan serve`의 실제 요청은 요청마다 애플리케이션이 새로 뜨므로 이 호출이 필요 없습니다.

## 4. 검증

`php artisan test --filter=TokenApiTest`

```
PASS  Tests\Feature\Api\TokenApiTest
✓ token can create and is rejected after logout

Tests: 1 passed (11 assertions)
```

틀린 비밀번호는 422, 토큰 없는 `POST /api/v1/posts`는 401, 작성자 토큰은 201, 다른 사용자는 403, 로그아웃 뒤 같은 토큰의 삭제는 401입니다.

실행 중인 서버에서 시드 계정으로 `POST /api/v1/login`을 호출하면 `token_type`은 Bearer이고 토큰 길이는 50자였습니다. 그 토큰으로 만든 글은 id 3, 작성자는 미나입니다. 토큰 없는 글쓰기는 401입니다.

다음 문서는 [study10.md](study10.md)입니다. 브라우저가 다른 포트에서 이 API를 부르도록 CORS를 열고 `js/`, `ts/` 화면을 둡니다.

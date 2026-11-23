# study14 · API 설계

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

REST·OpenAPI·버전·페이지·오류 규칙을 구현과 문서에 동일하게 고정한다.

## ② 📖 이론

REST는 URL을 자원으로, 메서드를 동작으로 표현한다. API 문서는 사람과 클라이언트가 함께 보는 계약서다. `/api/posts`는 목록/생성, `/api/posts/{id}`는 상세/부분 수정/삭제다. 공통 스펙 v1의 버전 이름을 OpenAPI info.version=1.0.0으로 기록하고 경로 /api를 기준으로 한다.

호환 경로 /api/v1은 예전 Resource·검증 방식 학습용이다. 새 필드 변경으로 기준 API를 깨야 한다면 새 버전과 폐기 일정을 설계한다. 단순히 같은 주소에서 data/meta 키를 바꾸지 않는다. Resource는 DB snake_case를 camelCase로 바꾸는 번역기이고 예외 응답 처리기는 오류를 같은 봉투에 넣는다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. /api-docs를 열어 로컬 Swagger UI와 /openapi.json을 확인한다. 자산은 npm 패키지로 빌드하므로 외부 CDN에 의존하지 않는다.
2. EntryResource·DocumentResource와 실제 응답 필드를 비교한다. 비밀번호·원문 문서·서버 파일 경로는 목록에 노출하지 않는다.
3. 목록 meta는 page/limit/total/totalPages/q다. page는 1부터, limit은 기본10·최대50이다. 정렬은 createdAt, -createdAt, -commentCount만 허용한다.
4. 400 검증 오류는 fields, 401 인증, 403 공개 글 소유권, 404 없는 자원/비공개 문서, 409 중복 이메일, 429 제한, 500/502/503 서비스 오류로 정리한다.
5. X-Request-Id를 응답 헤더와 error.requestId에 맞춘다. 요청 id는 길이와 안전한 문자만 허용하고 없으면 생성한다.
6. OpenAPI에서 Bearer를 넣어 요청할 때 로컬 학습 계정만 사용한다. 문서 UI는 토큰 영속 저장을 끈다.
7. 웹소켓 인증과 MCP는 각각 프로토콜 응답을 따르며 REST 오류 봉투로 MCP JSON-RPC를 덮어쓰지 않는다.

### 실행 명령

```powershell
cd project
php artisan route:list --path=api
php artisan test --compact --filter=ContractTest
curl.exe -i http://127.0.0.1:8001/openapi.json
# 전체 OpenAPI 원문: project/public/openapi.json (Git에 커밋됨)
```

명령은 위에서 아래로 실행한다. `cd`는 작업 폴더 이동, `php artisan`은 Laravel 작업, `composer`는 PHP 의존성, `npm`은 Vue 자산 도구, `docker compose`는 연결 서비스를 담당한다. 주석에 별도 터미널·운영 환경·선택 실습이 지정되어 있으면 그 경계를 유지한다.

### `project/app/Http/Resources/EntryResource.php` 전체 코드

[project/app/Http/Resources/EntryResource.php](project/app/Http/Resources/EntryResource.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class EntryResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return [
            'id' => $this->id, 'title' => $this->title, 'body' => $this->body,
            'tags' => $this->tags->pluck('name')->values(),
            'author' => $this->user ? ['id' => $this->user->id, 'nickname' => $this->user->name] : null,
            'commentCount' => (int) ($this->comments_count ?? 0),
            'createdAt' => $this->created_at?->utc()->toISOString(),
            'updatedAt' => $this->updated_at?->utc()->toISOString(),
        ];
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
| 7 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 8 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 9 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 10 | `toArray` 메서드를 선언한다. 모델 내부 속성을 외부 JSON 계약으로 변환한다. |
| 11 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 12 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 13 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 14 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 15 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 16 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 17 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 18 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 19 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 20 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 21 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `project/app/Http/Resources/DocumentResource.php` 전체 코드

[project/app/Http/Resources/DocumentResource.php](project/app/Http/Resources/DocumentResource.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Http\Resources;

use Illuminate\Http\Request;
use Illuminate\Http\Resources\Json\JsonResource;

class DocumentResource extends JsonResource
{
    public function toArray(Request $request): array
    {
        return ['id' => $this->id, 'userId' => $this->user_id, 'filename' => $this->filename,
            'status' => $this->status, 'summary' => $this->summary,
            'createdAt' => $this->created_at?->utc()->toISOString(),
            'updatedAt' => $this->updated_at?->utc()->toISOString()];
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
| 7 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 8 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 9 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 10 | `toArray` 메서드를 선언한다. 모델 내부 속성을 외부 JSON 계약으로 변환한다. |
| 11 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 12 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 13 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 14 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 15 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 16 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 17 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `project/bootstrap/app.php` 전체 코드

[project/bootstrap/app.php](project/bootstrap/app.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

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
    ->withBroadcasting(__DIR__.'/../routes/channels.php', ['prefix' => 'api', 'middleware' => ['api', 'auth:sanctum']])
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
| 20 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 21 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 22 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 23 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 24 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 25 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 26 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 27 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 28 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 29 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 30 | JSON 문자열을 구조화한 값으로 바꾸고 잘못된 입력을 처리한다. |
| 31 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 32 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 33 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 34 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 35 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 36 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 37 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 38 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 39 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 40 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 41 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 42 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 43 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 44 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 45 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 46 | 목록·청크·응답 스트림의 각 항목을 순서대로 처리한다. |
| 47 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 48 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 49 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 50 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 51 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 52 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 53 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 54 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |


### `project/app/Http/Middleware/RequestContext.php` 전체 코드

[project/app/Http/Middleware/RequestContext.php](project/app/Http/Middleware/RequestContext.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\Response;

class RequestContext
{
    public function handle(Request $request, Closure $next): Response
    {
        $id = $request->header('X-Request-Id');
        $id = is_string($id) && preg_match('/^[a-zA-Z0-9-]{1,80}$/', $id) ? $id : (string) Str::uuid();
        $request->attributes->set('requestId', $id);
        Log::withContext(['requestId' => $id]);
        if ($request->is('api/*') && ! $request->is('api/v1/*') && $request->isJson() && $request->getContent() !== '') {
            try {
                $json = json_decode($request->getContent(), true, 512, JSON_THROW_ON_ERROR);
                abort_unless(is_array($json), 400, 'BAD_REQUEST');
            } catch (\JsonException) {
                abort(400, 'BAD_REQUEST');
            }
        }
        $response = $next($request);
        $response->headers->set('X-Request-Id', $id);
        if (str_starts_with($response->headers->get('Content-Type', ''), 'application/json')) {
            $response->headers->set('Content-Type', 'application/json; charset=utf-8');
        }

        return $response;
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
| 10 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 11 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 12 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 13 | `handle` 메서드를 선언한다. 큐·미들웨어·MCP가 호출할 작업 진입점이다. |
| 14 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 15 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 16 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 17 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 18 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 19 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 20 | 실패 처리와 정리 동작을 분리해 부분 결과를 성공으로 취급하지 않는다. |
| 21 | JSON 문자열을 구조화한 값으로 바꾸고 잘못된 입력을 처리한다. |
| 22 | 조건이 참이 아니면 지정한 오류 상태로 요청을 중단한다. |
| 23 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 24 | 처리할 수 없는 요청을 명시적인 HTTP 오류로 중단한다. |
| 25 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 26 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 27 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 28 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 29 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 30 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 31 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 32 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 33 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 34 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 35 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `project/resources/js/docs.js` 전체 코드

[project/resources/js/docs.js](project/resources/js/docs.js)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```javascript
import SwaggerUI from 'swagger-ui-dist/swagger-ui-bundle.js';
import 'swagger-ui-dist/swagger-ui.css';
SwaggerUI({ url: '/openapi.json', dom_id: '#api-docs', persistAuthorization: false });
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 2 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 3 | 현재 메모리 토큰을 Bearer 인증 헤더에 연결한다. |


## ④ 🔗 연동 포인트

study12의 Vue는 이 계약의 실제 소비자다. 다음 단계의 캐시·큐는 내부 구현을 바꿔도 같은 API 계약을 유지해야 한다. 새 엔드포인트를 추가하면 OpenAPI와 계약 테스트를 함께 바꾼다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| meta.current_page를 읽어 페이지가 안 바뀜 | 새 화면이 이전 v1 형식을 사용 | 기준 /api의 meta.page로 맞춤 |
| 태그가 문자열로 전송됨 | 이전 입력 형태를 재사용 | tags 문자열 배열로 JSON 인코딩 |
| 500에 SQL이 보임 | 예외 원문을 API에 포함 | APP_DEBUG=false와 공통 오류 봉투 사용 |

## ⑥ 직접 해보기

1. Swagger UI에서 limit=1로 목록을 확인한다.
2. 위조 X-Request-Id에 제어문자를 넣지 못하도록 안전한 값 생성 분기를 확인한다.
3. OpenAPI와 실제 응답에서 createdAt과 error.fields를 대조한다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] 목록 `meta.current_page/last_page/total`을 `page/limit/total/totalPages`로 (API Resource 변환)
- [ ] 필드 이름 camelCase
- [ ] 오류 응답을 `error.code/message/fields`로 (예외 핸들러)
- [ ] OpenAPI 3와 실제 응답·인증을 대조했다.
- [ ] 버전 이름 v1과 기준 경로 /api를 구분했다.

## ⑧ 다음 단계 연결

REST·OpenAPI·버전·페이지·오류 규칙을 구현과 문서에 동일하게 고정한다. 이 결과를 [study15.md](study15.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://spec.openapis.org/oas/v3.0.3)
- [공식 문서 2](https://laravel.com/docs/13.x/errors)

# study6. 고급 기술 구현 1 — 게시글 JSON API

Blade가 그리던 글을 세션 없이 JSON으로도 읽습니다. 쓰기는 아직 열지 않습니다. 토큰 없는 쓰기 API는 study5에서 막은 손님 작성을 다시 여는 일이 되므로, 생성과 수정은 [study9.md](study9.md)의 Sanctum까지 미룹니다.

## 1. API 라우트를 연결한다

`bootstrap/app.php`의 `withRouting()`에 API 파일을 추가했습니다.

```php
api: __DIR__.'/../routes/api.php',
```

이 등록은 주소 앞에 `/api`를 붙입니다. `routes/api.php` 안의 `/v1/posts`는 실제 주소 `/api/v1/posts`입니다. 웹 미들웨어(세션, CSRF)는 타지 않습니다. `Accept: application/json`이면 오류도 JSON입니다. 스켈레톤이 `api/*` 요청을 JSON으로 그리도록 `shouldRenderJsonWhen`을 이미 넣어 두었습니다.

```php
Route::prefix('v1')->group(function () {
    Route::get('/posts', [PostController::class, 'index']);
    Route::get('/posts/{post}', [PostController::class, 'show']);
});
```

컨트롤러는 `App\Http\Controllers\Api\V1\PostController`입니다. 웹의 `PostController`와 클래스 이름이 같아도 네임스페이스가 다릅니다.

## 2. Resource가 응답 모양을 고정한다

모델 전체를 `json`으로 내보내면 `user_id`나 나중에 숨겨야 할 컬럼이 그대로 나갑니다. `PostResource`가 내보낼 키만 고릅니다.

```php
return [
    'id' => $this->id,
    'title' => $this->title,
    'body' => $this->body,
    'author' => $this->user?->name,
    'created_at' => $this->created_at?->toIso8601String(),
];
```

`PostResource::collection($posts)`와 `new PostResource($post)` 모두 바깥에 `data`를 둡니다. 작성자 이름은 `user` 관계를 미리 읽습니다. 비밀번호 컬럼은 이 배열에 없으므로 응답에 없습니다.

목록 순서는 `latest('id')`입니다. `created_at`만으로 정렬하면 같은 초에 만든 두 글의 순서가 흔들렸습니다. 테스트가 "나중" 대신 "먼저"를 받아서, 기본 키 내림차순으로 고정했습니다.

Blade의 `{{ }}`와 달리 JSON 본문은 HTML 이스케이프를 하지 않습니다. 화면에 넣을 때 이스케이프하는 쪽은 `js/`와 `ts/`입니다. 테스트는 본문에 태그 문자를 그대로 실어 이 차이를 확인합니다.

## 3. 검증

`php artisan test --filter=PostApiTest`

```
PASS  Tests\Feature\Api\PostApiTest
✓ posts are json and newest first
✓ one post is a resource

Tests: 2 passed (8 assertions)
```

없는 글 `GET /api/v1/posts/999`는 404입니다.

실행 중인 서버의 `GET /api/v1/posts`는 200이고, 첫 항목 작성자는 미나, 제목은 시드의 "세션 로그인은 쿠키다"입니다. 그 글의 id가 더 크기 때문입니다. 시각은 `+09:00`으로 나옵니다. study1의 서울 시간대가 API 날짜에도 적용된 결과입니다.

다음 문서는 [study7.md](study7.md)입니다. `/api/v1/posts/{post}/comments`로 댓글을 읽습니다.

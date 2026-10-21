# study7. 고급 기술 구현 2 — 중첩 댓글 API

댓글은 글에 속합니다. 주소도 글 아래에 둡니다. 웹의 `POST /posts/{post}/comments`와 같은 소속이고, 이 단계는 읽기만 엽니다.

## 1. 중첩 라우트

```php
Route::get('/posts/{post}/comments', [CommentController::class, 'index']);
```

실제 주소는 `/api/v1/posts/{post}/comments`입니다. `{post}`가 없으면 404입니다. 컨트롤러는 그 글의 `comments()`만 조회하므로 다른 글의 댓글이 섞이지 않습니다.

```php
$comments = $post->comments()->with('user')->orderBy('id')->get();

return CommentResource::collection($comments);
```

`CommentResource`는 `id`, `body`, `author`, `created_at`만 내보냅니다. `post_id`는 주소에 이미 있으므로 본문에서 뺐습니다.

순서는 id 오름차순입니다. 댓글은 먼저 단 것이 위에 있는 편이 읽기 자연스럽습니다. 글 목록의 최신순과 일부러 다르게 두었습니다.

## 2. 웹 라우트와의 차이

| | 웹 | API |
|---|---|---|
| 읽기 | `GET /posts/{post}` 안에 댓글을 포함 | 댓글만 따로 `GET` |
| 쓰기 | 세션이 있는 `POST` | study9에서 토큰이 있는 `POST` |
| 다른 글의 댓글 삭제 | `scopeBindings()`가 404 | 이 단계에는 삭제 라우트가 없음 |

한 응답에 글과 댓글을 같이 넣고 싶으면 `PostResource`에서 `CommentResource::collection($this->whenLoaded('comments'))`를 넣으면 됩니다. 지금은 클라이언트가 목록과 상세 댓글을 나눠 부르게 두었습니다. `js/`와 `ts/`가 그 두 요청을 순서대로 합니다.

## 3. 검증

`php artisan test --filter=CommentApiTest`

```
PASS  Tests\Feature\Api\CommentApiTest
✓ comments are nested under a post

Tests: 1 passed (5 assertions)
```

시드에는 1번 글의 댓글이 하나 있습니다. 실행 중인 서버의 `GET /api/v1/posts/1/comments`는 200, `data` 길이 1, 작성자는 미나입니다.

다음 문서는 [study8.md](study8.md)입니다. 같은 목록에 검색과 페이지를 넣습니다.

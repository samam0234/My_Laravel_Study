# study3. 실습3 — 라우팅, 컨트롤러, Blade CRUD

study2의 `Post`를 화면에 연결합니다. 로그인 없이 누구나 글을 쓰고 고칩니다. 작성자 제한은 [study5.md](study5.md)에서 넣습니다.

## 1. 리소스 라우트

`routes/web.php`에 한 줄을 추가했습니다.

```php
Route::resource('posts', PostController::class);
```

이 선언이 일곱 경로를 만듭니다. `{post}`는 라우트 모델 바인딩입니다. URL의 숫자가 `Post`의 기본 키와 같으면 컨트롤러 인자로 모델이 들어오고, 없으면 404입니다.

| 액션 | 메서드 | 경로 |
|---|---|---|
| index | GET | /posts |
| create | GET | /posts/create |
| store | POST | /posts |
| show | GET | /posts/{post} |
| edit | GET | /posts/{post}/edit |
| update | PUT/PATCH | /posts/{post} |
| destroy | DELETE | /posts/{post} |

웹 그룹이라 CSRF 검사가 켜져 있습니다. 폼은 `@csrf`를 넣습니다. 수정 폼은 `@method('PUT')`, 삭제 폼은 `@method('DELETE')`로 메서드를 속입니다. HTML 폼이 GET과 POST만 보내기 때문입니다.

## 2. 컨트롤러

`PostController`는 요청을 검증하고 모델을 부른 뒤 뷰를 고르거나 리다이렉트합니다.

```php
$data = $request->validate([
    'title' => ['required', 'string', 'max:120'],
    'body' => ['required', 'string'],
], [
    'title.required' => '제목을 입력해 주세요.',
    'body.required' => '내용을 입력해 주세요.',
]);

$post = Post::create($data);

return redirect()
    ->route('posts.show', $post)
    ->with('status', '글을 저장했습니다.');
```

`validate`가 실패하면 이전 페이지로 돌아가며 오류를 세션에 넣습니다. 성공하면 `with('status', ...)`가 다음 요청 한 번만 보이는 플래시 메시지입니다. 레이아웃이 `session('status')`를 출력합니다.

목록은 `Post::query()->latest()->get()`입니다. 페이지 나눔은 study8에서 API와 같이 넣습니다.

## 3. Blade

| 파일 | 역할 |
|---|---|
| `posts/index.blade.php` | 목록. 글이 없으면 "아직 글이 없습니다." |
| `posts/show.blade.php` | 한 건, 수정 링크, 삭제 폼 |
| `posts/create.blade.php` | 작성 |
| `posts/edit.blade.php` | 수정. 같은 폼 조각을 재사용 |
| `posts/_form.blade.php` | 제목, 내용, 오류 목록 |

`{{ $post->title }}`는 HTML을 이스케이프합니다. 레이아웃 상단에 게시판 링크를 넣었습니다.

Django 템플릿의 `{% url %}`, `{% csrf_token %}`에 해당하는 것이 `route()`와 `@csrf`입니다. Rails의 `form_with`가 토큰과 PATCH를 숨겨 주는 일을, Laravel에서는 `@csrf`와 `@method`로 화면에 드러냅니다.

## 4. 검증

`php artisan test --filter=PostCrudTest`

```
PASS  Tests\Feature\PostCrudTest
✓ index lists posts
✓ store validates and creates
✓ update and delete

Tests: 3 passed (19 assertions)
```

`php artisan serve`가 이미 떠 있는 상태에서 HTTP로도 확인했습니다.

| 요청 | 결과 |
|---|---|
| `GET /posts` | 200. 시드 제목 "Eloquent는 한 줄이 객체다" |
| `GET /posts/create` | 200. `name="title"` 입력 |
| `POST /posts` | 세션 쿠키와 `_token`을 실어 보냄. 302를 따라간 최종 주소 `/posts/3`, 200. 본문에 "HTTP로 저장한 글"과 "글을 저장했습니다." |

빈 제목은 테스트에서 `/posts/create`로 돌아오고 `title`, `body` 오류가 세션에 있습니다.

다음 문서는 [study4.md](study4.md)입니다. 글에 댓글을 `hasMany`로 붙입니다.

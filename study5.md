# study5. 실습5 — 세션 로그인과 작성자 권한

글과 댓글에 작성자를 붙이고, 세션으로 로그인합니다. Breeze나 Jetstream은 설치하지 않습니다. 그 패키지가 숨기는 `Auth::attempt`, 세션 재발급, `hashed` 캐스트, `auth` 미들웨어를 코드로 먼저 봅니다.

## 1. 작성자 컬럼은 새 마이그레이션이다

study2에서 만든 `posts`를 고치지 않고 `2026_10_21_000003_add_user_foreign_keys`를 추가했습니다. 이미 들어 있는 글을 깨지 않으려고 `user_id`는 nullable입니다. 새로 쓰는 글은 컨트롤러가 항상 로그인 사용자를 넣습니다.

```php
$table->foreignId('user_id')->nullable()->after('id')->constrained()->nullOnDelete();
```

댓글 테이블에도 같은 컬럼을 넣었습니다. `nullOnDelete()`는 사용자를 지워도 글 행은 남고 `user_id`만 비웁니다. 글 삭제가 댓글을 지우는 `cascadeOnDelete()`와는 방향이 다릅니다.

시드는 `mina@example.com` / `password123`과 글 두 개, 댓글 하나를 만듭니다. `User`의 `password` 캐스트가 `hashed`라 시드에 평문을 넣어도 테이블에는 해시가 저장됩니다. 개발 DB는 `php artisan migrate:fresh --seed`로 다시 만들었습니다.

## 2. 직접 만든 로그인

| 주소 | 미들웨어 | 하는 일 |
|---|---|---|
| GET/POST `/register` | guest | 회원 생성 후 `Auth::login` |
| GET/POST `/login` | guest | `Auth::attempt` |
| POST `/logout` | auth | 세션 무효화, CSRF 토큰 재발급 |

로그인이 성공하면 `session()->regenerate()`로 세션 id를 바꿉니다. 로그인 전에 심어 둔 세션 id를 그대로 쓰지 않게 하려는 단계입니다. 실패하면 "이메일 또는 비밀번호가 올바르지 않습니다."를 세션 오류로 돌립니다.

비밀번호 확인은 `confirmed` 규칙입니다. 폼 필드는 `password_confirmation`입니다.

글쓰기, 글 수정, 글 삭제, 댓글 작성, 댓글 삭제는 `auth` 미들웨어 뒤에 있습니다. 손님은 `/login`으로 갑니다. 목록과 상세는 그대로 공개입니다.

`user_id`는 fillable에 없습니다. 글은 `$request->user()->posts()->create($data)`로 만들고, 댓글은 `associate($request->user())`로 작성자를 붙입니다. 요청 본문에 다른 사용자 번호를 넣어도 작성자가 바뀌지 않습니다.

## 3. Policy

```php
public function update(User $user, Post $post): bool
{
    return $post->user_id === $user->id;
}
```

`PostPolicy`의 `delete`는 `update`와 같습니다. `CommentPolicy`는 `delete`만 있습니다. 컨트롤러는 `$this->authorize('update', $post)`를 부릅니다. 작성자가 아니면 403입니다. Blade는 `@can('update', $post)`로 수정·삭제 폼을 숨깁니다.

### Breeze, Jetstream과 대응

| 직접 구현 | Breeze가 생성하는 것 |
|---|---|
| `RegisteredUserController` | `app/Http/Controllers/Auth/RegisteredUserController.php` |
| `SessionController` | `AuthenticatedSessionController` |
| `auth` / `guest` 미들웨어 | 같은 미들웨어. 라우트 파일만 갈라 둠 |
| Blade 폼 | Blade 스택. React/Vue 스택은 Inertia 화면 |
| 없음 | 비밀번호 재설정, 이메일 인증 |

Jetstream은 여기서 더 나갑니다. 팀, 프로필 사진, 2단계 인증이 들어 있습니다. 이 게시판에는 그 기능이 없습니다. Fortify는 화면 없이 위 컨트롤러의 백엔드만 제공합니다. Breeze의 Laravel 쪽 인증은 Fortify 위에서 도는 경우가 많습니다.

## 4. 맞닥뜨린 오류

Laravel 13 스켈레톤의 `Controller`는 빈 클래스입니다. `$this->authorize()`를 부르면 `Call to undefined method Controller::authorize()`가 납니다. `AuthorizesRequests` 트레이트를 베이스 컨트롤러에 넣어야 Policy 호출이 동작합니다.

라우트 순서도 한 번 틀렸습니다. `GET /posts/{post}`를 `GET /posts/create`보다 먼저 등록하면 주소의 `create`가 글 번호로 바인딩되고, 글이 없어 404가 납니다. 로그인 리다이렉트까지 가지 못합니다. 인증이 필요한 `create` 라우트를 `{post}`보다 먼저 등록해 고쳤습니다.

## 5. 검증

`php artisan test`는 14개, 62개 단언이 통과했습니다. 이번 단계에서 추가한 확인은 아래입니다.

- 손님의 `GET /posts/create`와 `POST /posts`는 `/login`으로 갑니다.
- 가입하면 비밀번호가 해시로 저장되고 세션이 열립니다.
- 틀린 비밀번호는 `email` 오류입니다. 맞는 비밀번호 뒤 `POST /logout`은 손님으로 되돌립니다.
- 다른 사용자의 `PUT /posts/{id}`는 403입니다. 작성자의 수정과 삭제는 통과합니다.

실행 중인 서버에서 손님 `GET /posts/create`는 302, `Location`은 `http://127.0.0.1:8000/login`이었습니다. `POST /login`에 시드 계정을 넣으면 302로 `/posts`에 가고, 다음 목록 응답에 "미나"와 "로그아웃"이 있습니다.

다음 문서는 [study6.md](study6.md)입니다. 같은 글을 세션 없이 읽는 JSON API를 엽니다. 쓰기 토큰은 study9의 Sanctum까지 기다립니다.

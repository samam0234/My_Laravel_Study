# study4. 실습4 — Eloquent 관계와 댓글

글 아래에 댓글을 둡니다. 한 글이 댓글을 여러 개 가지고, 댓글은 글 하나에 속합니다. 로그인 사용자는 아직 없습니다.

## 1. 마이그레이션

`comments.post_id`는 `posts.id`를 가리킵니다. 글을 지우면 댓글도 지웁니다.

```php
$table->foreignId('post_id')->constrained()->cascadeOnDelete();
$table->text('body');
```

`constrained()`는 컬럼 이름 `post_id`에서 `posts` 테이블을 추론합니다. `cascadeOnDelete()`는 데이터베이스 외래 키 규칙입니다. 모델의 `deleting` 이벤트를 따로 적지 않습니다.

```powershell
php artisan migrate
```

적용 기록: `2026_10_21_000002_create_comments_table`.

## 2. 양쪽 모델에 관계를 적는다

```php
public function comments(): HasMany
{
    return $this->hasMany(Comment::class);
}
```

```php
public function post(): BelongsTo
{
    return $this->belongsTo(Post::class);
}
```

댓글을 만들 때는 관계로 저장합니다. `post_id`는 fillable에 없습니다. `$post->comments()->create(['body' => ...])`가 외래 키를 채웁니다. 클라이언트가 다른 글 번호를 본문에 섞어도 그 키는 버려지고, 주소의 `{post}`가 부모가 됩니다.

Rails의 `has_many :comments` / `belongs_to :post`, Django의 `ForeignKey(Post)`와 같은 선언입니다. Laravel은 "여러 개" 쪽과 "하나" 쪽을 양쪽 모델에 메서드로 적습니다.

## 3. 주소는 글 아래에 댓글을 둔다

```php
Route::post('/posts/{post}/comments', [CommentController::class, 'store'])
    ->name('posts.comments.store');
Route::delete('/posts/{post}/comments/{comment}', [CommentController::class, 'destroy'])
    ->scopeBindings()
    ->name('posts.comments.destroy');
```

`scopeBindings()`는 `{comment}`를 그 `{post}`의 댓글로 제한합니다. 다른 글의 댓글 id로 지우면 404입니다.

목록은 `withCount('comments')`로 개수만 가져옵니다. 상세는 `load(['comments' => fn ($query) => $query->oldest()])`로 댓글 본문을 한 번에 읽습니다. 글마다 댓글 쿼리를 다시 날리지 않으려고입니다.

화면은 `posts/show.blade.php` 아래 폼입니다. `@csrf`와 `body` 검증(`required`, 최대 1000자)을 통과해야 저장됩니다.

## 4. 검증

`php artisan test --filter=CommentTest`

```
PASS  Tests\Feature\CommentTest
✓ a post has many comments
✓ comment can be stored and deleted on its post
✓ deleting a post deletes its comments

Tests: 3 passed (12 assertions)
```

실행 중인 서버에서 `POST /posts/3/comments`에 세션과 CSRF를 실어 "실서버 댓글"을 저장했습니다. 최종 주소는 `/posts/3`이고 본문에 댓글과 "댓글을 저장했습니다."가 있습니다.

다음 문서는 [study5.md](study5.md)입니다. 세션 로그인을 직접 만들고, 작성자만 글과 댓글을 고치게 합니다.

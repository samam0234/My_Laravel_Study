# study2. 실습2 — Eloquent 모델과 마이그레이션

화면은 아직 바꾸지 않습니다. `posts` 테이블과 `Post` 모델이 생기고, 시드 두 건이 들어가는 것이 이번 실습의 끝입니다. Blade CRUD는 [study3.md](study3.md)에서 붙입니다.

## 1. 마이그레이션이 스키마를 가진다

모델 파일에는 컬럼 정의를 적지 않습니다. `database/migrations/2026_10_21_000001_create_posts_table.php`가 테이블을 만듭니다.

```php
Schema::create('posts', function (Blueprint $table) {
    $table->id();
    $table->string('title');
    $table->text('body');
    $table->timestamps();
});
```

`id()`는 정수 기본 키입니다. `timestamps()`는 `created_at`, `updated_at`입니다. 작성자 컬럼은 로그인 실습에서 새 마이그레이션으로 추가합니다. 이미 적용한 파일을 고치지 않는 약속입니다.

```powershell
php artisan migrate
```

개발 DB에 이 파일이 적용된 기록은 `migrations` 테이블에 남습니다. 테스트는 `RefreshDatabase`가 메모리 SQLite에 같은 마이그레이션을 다시 돌립니다. `phpunit.xml`의 `DB_DATABASE=:memory:` 때문입니다.

Rails의 `rails db:migrate`, Django의 `migrate`와 같은 명령입니다.

## 2. 모델은 한 줄을 객체로 다룬다

```php
#[Fillable(['title', 'body'])]
class Post extends Model
{
    /** @use HasFactory<PostFactory> */
    use HasFactory;
}
```

`#[Fillable]`은 `Post::create()`와 `update()`가 받을 키입니다. 요청에 `id`를 섞어도 그 값은 버려집니다. Laravel 13 스켈레톤의 `User`도 같은 속성을 씁니다. 예전 자료의 `protected $fillable`과 같은 일입니다.

팩토리는 `database/factories/PostFactory.php`입니다. 테스트에서 `Post::factory()->create()`로 쓸 수 있게 HasFactory를 붙였습니다. 이번 테스트는 컬럼을 분명히 보이려고 `Post::create()`를 직접 호출합니다.

## 3. 시드

`DatabaseSeeder`가 글 두 개를 넣습니다. 스켈레톤의 테스트 사용자는 그대로 두었습니다. 로그인에 쓰는 계정은 study5에서 바꿉니다.

```powershell
php artisan db:seed
```

시드 뒤 `Post::count()`는 2이고, 마지막 제목은 "Blade는 다음 실습에서 붙인다"입니다.

## 4. 검증

`php artisan test --filter=PostModelTest`

```
PASS  Tests\Feature\PostModelTest
✓ a post row is a model
✓ columns outside fillable are ignored

Tests: 2 passed (3 assertions)
```

만든 글의 `created_at` 시간대 이름은 `Asia/Seoul`입니다. study1에서 고정한 앱 시간대가 Eloquent 날짜 캐스트까지 이어진 결과입니다. `id`에 99를 넣어 생성해도 저장된 기본 키는 99가 아닙니다.

`php artisan migrate` 출력:

```
2026_10_21_000001_create_posts_table  DONE
```

다음 문서는 [study3.md](study3.md)입니다. 이 모델을 리소스 라우트와 Blade로 목록, 작성, 수정, 삭제합니다.

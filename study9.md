# study9 · 테스트·디버깅

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

순수 단위 테스트와 DB·HTTP 요청 테스트로 실패 원인을 재현한다.

## ② 📖 이론

단위 테스트는 작은 계산을 빠르게 확인하고 Feature 테스트는 요청·인증·검증·DB·응답의 연결을 확인한다. 부품 검사와 조립품 검사에 비유할 수 있다. TagNamesTest는 PHP 순수 함수, ContractTest는 실제 SQLite DB와 HTTP 계약을 검증한다.

테스트 DB는 메모리 SQLite이며 실제 학습 DB를 지우지 않는다. 외부 API는 Http::fake와 preventStrayRequests, 파일은 Storage::fake, 큐는 Queue::fake, 알림은 Notification::fake로 바꾼다. DB 쿼리 빌더 자체를 mock하면 SQL 실수를 놓치므로 실제 테스트 DB를 사용한다. project의 DocumentTest는 AI·파일·큐 가짜를 연결한 심화 예제다.

디버깅 순서는 재현 요청 → 상태 코드 → error.requestId → storage/logs/laravel.log → 좁은 테스트다. 개발자도구 Network는 요청 본문과 응답, Console은 Vue 오류, php artisan route:list는 URL, php artisan pail은 로그를 보여 준다. 운영 로그에 비밀번호·토큰·문서 전문을 남기지 않는다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. TagNamesTest만 실행해 순수 규칙을 확인한다. 테스트가 실제 사용할 문자열 0과 유니코드 경계를 다루는 이유를 읽는다.
2. ContractTest는 가입·로그인·소유권·페이지·부분 수정·로그아웃·댓글·캐시를 검증한다. 요청 결과와 DB 변경을 함께 단언한다.
3. project의 DocumentTest에서 Http::preventStrayRequests가 실제 AI 호출을 막고 NDJSON 스트림만 가짜로 주는 부분을 찾는다.
4. 실패 테스트 하나를 수정한 뒤 그 테스트부터 다시 실행한다. 마지막에 전체 앱 테스트를 한 번 실행해 회귀를 확인한다.
5. 아래 TOP 10을 증상별 시작점으로 사용한다. 토큰을 바꾸는 한 테스트 안에서는 forgetGuards가 이전 사용자를 초기화한다.

### 실행 명령

```powershell
cd demo
php artisan test --compact --filter=TagNamesTest
php artisan test --compact --filter=ContractTest
php artisan test --compact
Get-Content storage/logs/laravel.log -Tail 30
# project에서는 php artisan test --compact --filter=DocumentTest
```

명령은 위에서 아래로 실행한다. `cd`는 작업 폴더 이동, `php artisan`은 Laravel 작업, `composer`는 PHP 의존성, `npm`은 Vue 자산 도구, `docker compose`는 연결 서비스를 담당한다. 주석에 별도 터미널·운영 환경·선택 실습이 지정되어 있으면 그 경계를 유지한다.

### `demo/tests/Unit/TagNamesTest.php` 전체 코드

[demo/tests/Unit/TagNamesTest.php](demo/tests/Unit/TagNamesTest.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace Tests\Unit;

use App\Support\TagNames;
use PHPUnit\Framework\TestCase;

class TagNamesTest extends TestCase
{
    public function test_normalization_trims_deduplicates_and_keeps_string_zero(): void
    {
        $this->assertSame(['Laravel', '0'], TagNames::normalize([' Laravel ', '', 'Laravel', '0']));
    }

    public function test_normalization_limits_unicode_length_and_number_of_tags(): void
    {
        $names = [str_repeat('한', 40), ...array_map(fn ($n) => '태그'.$n, range(1, 10))];
        $actual = TagNames::normalize($names);
        $this->assertCount(8, $actual);
        $this->assertSame(str_repeat('한', 30), $actual[0]);
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
| 10 | `test_normalization_trims_deduplicates_and_keeps_string_zero` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 11 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 12 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 13 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 14 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 15 | `test_normalization_limits_unicode_length_and_number_of_tags` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 16 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 17 | 각 원소에 같은 변환을 적용한다. |
| 18 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 19 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 20 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 21 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 22 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `demo/tests/Feature/ContractTest.php` 전체 코드

[demo/tests/Feature/ContractTest.php](demo/tests/Feature/ContractTest.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Hash;
use Tests\TestCase;

class ContractTest extends TestCase
{
    use RefreshDatabase;

    public function test_signup_hashes_password_and_returns_201_with_camel_case_token(): void
    {
        $result = $this->postJson('/api/auth/signup', ['nickname' => '학습자', 'email' => 'student@example.com', 'password' => 'a-long-password']);
        $result->assertCreated()->assertJsonPath('data.user.nickname', '학습자')->assertJsonMissingPath('data.user.password');
        $this->assertDatabaseHas('users', ['email' => 'student@example.com']);
        $this->assertTrue(Hash::check('a-long-password', User::query()->first()->password));
        $this->assertNotEmpty($result->json('data.accessToken'));
    }

    public function test_duplicate_email_returns_409_without_creating_a_second_user(): void
    {
        $user = User::factory()->create();
        $this->postJson('/api/auth/signup', ['nickname' => '중복', 'email' => $user->email, 'password' => 'a-long-password'])
            ->assertConflict()->assertJsonPath('error.code', 'EMAIL_TAKEN');
        $this->assertDatabaseCount('users', 1);
    }

    public function test_invalid_login_returns_401(): void
    {
        $this->postJson('/api/auth/login', ['email' => 'missing@example.com', 'password' => 'wrong'])
            ->assertUnauthorized()->assertJsonPath('error.code', 'INVALID_CREDENTIALS');
        $this->assertDatabaseCount('personal_access_tokens', 0);
    }

    public function test_missing_token_returns_401_with_matching_request_id(): void
    {
        $this->withHeader('X-Request-Id', 'course-test')->postJson('/api/posts', ['title' => 'test'])
            ->assertUnauthorized()->assertHeader('X-Request-Id', 'course-test')->assertJsonPath('error.requestId', 'course-test');
        $this->assertDatabaseCount('posts', 0);
    }

    public function test_partial_update_keeps_body_and_tags_and_rejects_foreign_owner(): void
    {
        $owner = User::factory()->create();
        $other = User::factory()->create();
        $token = $owner->createToken('test')->plainTextToken;
        $created = $this->withToken($token)->postJson('/api/posts', ['title' => '첫 글', 'body' => '그대로', 'tags' => ['study'], 'user_id' => $other->id]);
        $created->assertCreated()->assertJsonPath('data.author.id', $owner->id)->assertJsonPath('data.tags', ['study']);
        $id = $created->json('data.id');
        $created->assertHeader('Location', '/api/posts/'.$id);
        $this->patchJson('/api/posts/'.$id, ['title' => '제목만'])->assertOk()->assertJsonPath('data.body', '그대로')->assertJsonPath('data.tags', ['study']);
        $this->assertDatabaseHas('posts', ['id' => $id, 'title' => '제목만', 'body' => '그대로', 'user_id' => $owner->id]);
        $this->app['auth']->forgetGuards();
        $this->withToken($other->createToken('test')->plainTextToken)->deleteJson('/api/posts/'.$id)->assertForbidden()->assertJsonPath('error.code', 'FORBIDDEN');
        $this->assertDatabaseHas('posts', ['id' => $id]);
    }

    public function test_list_uses_spec_meta_and_rejects_sql_sort_input(): void
    {
        $user = User::factory()->create();
        $relation = config('study.relation');
        foreach (['Laravel A', 'Laravel B', '다른 글'] as $title) {
            $user->{$relation}()->create(['title' => $title, 'body' => '본문']);
        }
        $this->getJson('/api/posts?q=Laravel&limit=1&page=2&sort=createdAt')->assertOk()
            ->assertJsonCount(1, 'data')->assertJsonPath('meta', ['page' => 2, 'limit' => 1, 'total' => 2, 'totalPages' => 2, 'q' => 'Laravel'])
            ->assertJsonPath('data.0.title', 'Laravel B')->assertJsonMissingPath('data.0.created_at');
        $this->getJson('/api/posts?sort=title%20desc')->assertBadRequest()->assertJsonPath('error.code', 'VALIDATION_ERROR');
        $this->getJson('/api/posts?limit=999')->assertOk()->assertJsonPath('meta.limit', 50);
    }

    public function test_validation_returns_400_and_never_writes_invalid_record(): void
    {
        $user = User::factory()->create();
        $this->withToken($user->createToken('test')->plainTextToken)->postJson('/api/posts', [])
            ->assertBadRequest()->assertJsonPath('error.code', 'VALIDATION_ERROR')->assertJsonStructure(['error' => ['fields' => ['title', 'body']]]);
        $this->assertDatabaseCount('posts', 0);
    }

    public function test_malformed_json_returns_400(): void
    {
        $this->call('POST', '/api/auth/login', [], [], [], ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'], '{broken')
            ->assertBadRequest()->assertJsonPath('error.code', 'BAD_REQUEST');
        $this->call('POST', '/api/auth/login', [], [], [], ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json'], 'null')
            ->assertBadRequest()->assertJsonPath('error.code', 'BAD_REQUEST');
    }

    public function test_logout_revokes_the_token_and_expired_token_returns_401(): void
    {
        $user = User::factory()->create();
        $token = $user->createToken('test')->plainTextToken;
        $this->withToken($token)->getJson('/api/auth/me')->assertOk()->assertJsonPath('data.nickname', $user->name);
        $this->postJson('/api/auth/logout')->assertNoContent();
        $this->app['auth']->forgetGuards();
        $this->withToken($token)->getJson('/api/auth/me')->assertUnauthorized();
        $this->app['auth']->forgetGuards();
        $expired = $user->createToken('expired', ['*'], now()->subMinute())->plainTextToken;
        $this->withToken($expired)->getJson('/api/auth/me')->assertUnauthorized();
    }

    public function test_missing_route_returns_404_without_exception_details(): void
    {
        $this->getJson('/api/missing')->assertNotFound()->assertJsonPath('error.code', 'NOT_FOUND')->assertJsonMissingPath('exception');
    }

    public function test_comments_follow_the_same_contract_and_only_author_can_delete(): void
    {
        $owner = User::factory()->create();
        $other = User::factory()->create();
        $relation = config('study.relation');
        $entry = $owner->{$relation}()->create(['title' => '글', 'body' => '본문']);
        $this->withToken($owner->createToken('comments')->plainTextToken);
        $response = $this->postJson('/api/posts/'.$entry->id.'/comments', ['body' => '첫 댓글']);
        $response->assertCreated()->assertJsonPath('data.author.id', $owner->id)->assertJsonPath('data.postId', $entry->id);
        $id = $response->json('data.id');
        $this->getJson('/api/posts/'.$entry->id)->assertOk()->assertJsonPath('data.commentCount', 1);
        $this->patchJson('/api/posts/'.$entry->id, ['title' => '댓글 유지'])->assertOk()->assertJsonPath('data.commentCount', 1);
        $this->getJson('/api/posts/'.$entry->id.'/comments')->assertOk()->assertJsonPath('data.0.body', '첫 댓글');
        $this->app['auth']->forgetGuards();
        $this->withToken($other->createToken('comments')->plainTextToken)->deleteJson('/api/comments/'.$id)->assertForbidden();
        $this->assertDatabaseHas('comments', ['id' => $id, 'body' => '첫 댓글']);
        $this->app['auth']->forgetGuards();
        $this->withToken($owner->createToken('comments')->plainTextToken)->deleteJson('/api/comments/'.$id)->assertNoContent();
        $this->assertDatabaseMissing('comments', ['id' => $id]);
    }

    public function test_cached_total_is_invalidated_after_creating_and_deleting(): void
    {
        $user = User::factory()->create();
        $this->getJson('/api/stats')->assertOk()->assertJsonPath('data.total', 0);
        $created = $this->withToken($user->createToken('stats')->plainTextToken)->postJson('/api/posts', ['title' => '캐시', 'body' => '변경']);
        $created->assertCreated();
        $id = $created->json('data.id');
        $this->getJson('/api/stats')->assertOk()->assertJsonPath('data.total', 1);
        $this->deleteJson('/api/posts/'.$id)->assertNoContent();
        $this->getJson('/api/stats')->assertOk()->assertJsonPath('data.total', 0);
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
| 9 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 10 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 11 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 12 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 13 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 14 | `test_signup_hashes_password_and_returns_201_with_camel_case_token` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 15 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 16 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 17 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 18 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 19 | 모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다. |
| 20 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 21 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 22 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 23 | `test_duplicate_email_returns_409_without_creating_a_second_user` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 24 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 25 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 26 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 27 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 28 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 29 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 30 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 31 | `test_invalid_login_returns_401` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 32 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 33 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 34 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 35 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 36 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 37 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 38 | `test_missing_token_returns_401_with_matching_request_id` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 39 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 40 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 41 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 42 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 43 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 44 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 45 | `test_partial_update_keeps_body_and_tags_and_rejects_foreign_owner` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 46 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 47 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 48 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 49 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 50 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 51 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 52 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 53 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 54 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 55 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 56 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 57 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 58 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 59 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 60 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 61 | `test_list_uses_spec_meta_and_rejects_sql_sort_input` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 62 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 63 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 64 | 환경에 맞게 로드한 설정값을 읽는다. |
| 65 | 목록·청크·응답 스트림의 각 항목을 순서대로 처리한다. |
| 66 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 67 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 68 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 69 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 70 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 71 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 72 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 73 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 74 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 75 | `test_validation_returns_400_and_never_writes_invalid_record` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 76 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 77 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 78 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 79 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 80 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 81 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 82 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 83 | `test_malformed_json_returns_400` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 84 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 85 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 86 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 87 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 88 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 89 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 90 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 91 | `test_logout_revokes_the_token_and_expired_token_returns_401` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 92 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 93 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 94 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 95 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 96 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 97 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 98 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 99 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 100 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 101 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 102 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 103 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 104 | `test_missing_route_returns_404_without_exception_details` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 105 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 106 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 107 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 108 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 109 | `test_comments_follow_the_same_contract_and_only_author_can_delete` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 110 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 111 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 112 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 113 | 환경에 맞게 로드한 설정값을 읽는다. |
| 114 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 115 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 116 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 117 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 118 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 119 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 120 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 121 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 122 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 123 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 124 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 125 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 126 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 127 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 128 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 129 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 130 | `test_cached_total_is_invalidated_after_creating_and_deleting` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 131 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 132 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 133 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 134 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 135 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 136 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 137 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 138 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 139 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 140 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 141 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `project/tests/Feature/DocumentTest.php` 전체 코드

[project/tests/Feature/DocumentTest.php](project/tests/Feature/DocumentTest.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace Tests\Feature;

use App\Jobs\SummarizeDocument;
use App\Models\Document;
use App\Models\User;
use App\Notifications\DocumentReady;
use App\Services\DocumentAi;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Notification;
use Illuminate\Support\Facades\Queue;
use Illuminate\Support\Facades\Storage;
use Tests\TestCase;

class DocumentTest extends TestCase
{
    use RefreshDatabase;

    public function test_upload_returns_202_stores_private_file_and_queues_owner_document(): void
    {
        $user = User::factory()->create();
        Storage::fake('local');
        Queue::fake([SummarizeDocument::class]);
        $this->withToken($user->createToken('test')->plainTextToken)->post('/api/documents', ['file' => UploadedFile::fake()->createWithContent('study.txt', 'Laravel 문서 요약 연습입니다.')], ['Accept' => 'application/json'])
            ->assertAccepted()->assertJsonPath('data.userId', $user->id)->assertJsonMissingPath('data.content')->assertJsonMissingPath('data.path');
        $document = Document::query()->firstOrFail();
        Storage::disk('local')->assertExists($document->path);
        Queue::assertPushed(SummarizeDocument::class, fn ($job) => $job->documentId === $document->id);
        $this->assertDatabaseHas('documents', ['id' => $document->id, 'status' => 'queued']);
    }

    public function test_unsupported_file_returns_400_and_does_not_dispatch(): void
    {
        $user = User::factory()->create();
        Storage::fake('local');
        Queue::fake([SummarizeDocument::class]);
        $this->withToken($user->createToken('test')->plainTextToken)->post('/api/documents', ['file' => UploadedFile::fake()->createWithContent('attack.php', '<?php echo 1;')], ['Accept' => 'application/json'])->assertBadRequest();
        $this->assertDatabaseCount('documents', 0);
        Queue::assertNotPushed(SummarizeDocument::class);
    }

    public function test_foreign_document_is_hidden_from_list_download_delete_and_ask(): void
    {
        $document = Document::factory()->create();
        $other = User::factory()->create();
        $this->withToken($other->createToken('test')->plainTextToken)->getJson('/api/documents')->assertOk()->assertJsonCount(0, 'data');
        $this->getJson('/api/documents/'.$document->id.'/download')->assertNotFound();
        $this->deleteJson('/api/documents/'.$document->id)->assertNotFound();
        $this->postJson('/api/documents/'.$document->id.'/ask', ['question' => '문서'])->assertNotFound();
        $this->assertModelExists($document);
    }

    public function test_summary_job_persists_summary_and_sends_notification_once(): void
    {
        $document = Document::factory()->create();
        Notification::fake();
        config(['study.ai_driver' => 'mock']);
        $job = new SummarizeDocument($document->id);
        $job->handle(app(DocumentAi::class));
        $job->handle(app(DocumentAi::class));
        $this->assertDatabaseHas('documents', ['id' => $document->id, 'status' => 'ready']);
        $this->assertStringContainsString('[mock 실습]', $document->fresh()->summary);
        Notification::assertSentToTimes($document->user, DocumentReady::class, 1);
    }

    public function test_ask_streams_deltas_and_saves_grounded_history(): void
    {
        $document = Document::factory()->create();
        config(['study.ai_driver' => 'mock']);
        $response = $this->withToken($document->user->createToken('test')->plainTextToken)->postJson('/api/documents/'.$document->id.'/ask', ['question' => 'Laravel 문서']);
        $response->assertOk()->assertHeader('Content-Type', 'text/event-stream; charset=UTF-8');
        $stream = $response->streamedContent();
        $this->assertStringContainsString('"done":true', $stream);
        $this->assertStringContainsString('"delta":', $stream);
        $this->assertDatabaseHas('document_questions', ['document_id' => $document->id, 'question' => 'Laravel 문서']);
    }

    public function test_ollama_ndjson_stream_is_relayed_without_network(): void
    {
        config(['study.ai_driver' => 'ollama', 'study.ai_url' => 'http://ollama.test']);
        Http::preventStrayRequests();
        Http::fake(['http://ollama.test/api/chat' => Http::response("{\"message\":{\"content\":\"첫 토큰\"},\"done\":false}\n{\"message\":{\"content\":\" 끝\"},\"done\":true}\n", 200)]);
        $answer = implode('', iterator_to_array(app(DocumentAi::class)->stream('근거', '질문')));
        $this->assertSame('첫 토큰 끝', $answer);
        Http::assertSent(fn ($request) => $request['stream'] === true && $request['messages'][0]['role'] === 'system');
    }

    public function test_ollama_disconnect_emits_error_and_does_not_store_partial_answer(): void
    {
        $document = Document::factory()->create();
        config(['study.ai_driver' => 'ollama', 'study.ai_url' => 'http://ollama.test']);
        Http::preventStrayRequests();
        Http::fake(['http://ollama.test/api/chat' => Http::response('offline', 503)]);
        $response = $this->withToken($document->user->createToken('test')->plainTextToken)->postJson('/api/documents/'.$document->id.'/ask', ['question' => 'Laravel']);
        $response->assertOk();
        $this->assertStringContainsString('"error":', $response->streamedContent());
        $this->assertDatabaseCount('document_questions', 0);
        Http::assertSentCount(1);
    }

    public function test_mcp_requires_auth_and_hides_foreign_document(): void
    {
        $document = Document::factory()->create();
        $other = User::factory()->create();
        $payload = ['jsonrpc' => '2.0', 'id' => 1, 'method' => 'tools/call', 'params' => ['name' => 'read-document', 'arguments' => ['id' => $document->id]]];
        $this->postJson('/mcp/library', $payload)->assertUnauthorized();
        $this->withToken($other->createToken('mcp')->plainTextToken)->postJson('/mcp/library', $payload)
            ->assertOk()->assertJsonPath('result.isError', true)->assertJsonPath('result.content.0.text', 'Document not found');
        $this->app['auth']->forgetGuards();
        $this->withToken($document->user->createToken('mcp')->plainTextToken)->postJson('/mcp/library', $payload)
            ->assertOk()->assertJsonPath('result.content.0.text', $document->content);
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
| 10 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 11 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 12 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 13 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 14 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 15 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 16 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 17 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 18 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 19 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 20 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 21 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 22 | `test_upload_returns_202_stores_private_file_and_queues_owner_document` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 23 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 24 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 25 | 비공개 저장 디스크를 통해 파일을 읽고 쓰거나 내려받는다. |
| 26 | 테스트에 필요한 외부 부작용을 프레임워크 가짜로 대체한다. |
| 27 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 28 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 29 | 모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다. |
| 30 | 비공개 저장 디스크를 통해 파일을 읽고 쓰거나 내려받는다. |
| 31 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 32 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 33 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 34 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 35 | `test_unsupported_file_returns_400_and_does_not_dispatch` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 36 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 37 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 38 | 비공개 저장 디스크를 통해 파일을 읽고 쓰거나 내려받는다. |
| 39 | 테스트에 필요한 외부 부작용을 프레임워크 가짜로 대체한다. |
| 40 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 41 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 42 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 43 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 44 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 45 | `test_foreign_document_is_hidden_from_list_download_delete_and_ask` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 46 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 47 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 48 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 49 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 50 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 51 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 52 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 53 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 54 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 55 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 56 | `test_summary_job_persists_summary_and_sends_notification_once` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 57 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 58 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 59 | 테스트에 필요한 외부 부작용을 프레임워크 가짜로 대체한다. |
| 60 | 환경에 맞게 로드한 설정값을 읽는다. |
| 61 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 62 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 63 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 64 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 65 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 66 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 67 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 68 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 69 | `test_ask_streams_deltas_and_saves_grounded_history` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 70 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 71 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 72 | 환경에 맞게 로드한 설정값을 읽는다. |
| 73 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 74 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 75 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 76 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 77 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 78 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 79 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 80 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 81 | `test_ollama_ndjson_stream_is_relayed_without_network` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 82 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 83 | 환경에 맞게 로드한 설정값을 읽는다. |
| 84 | 가짜로 지정하지 않은 외부 HTTP가 나가지 못하게 막는다. |
| 85 | 지정한 외부 HTTP 응답을 테스트 가짜로 바꾼다. |
| 86 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 87 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 88 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 89 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 90 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 91 | `test_ollama_disconnect_emits_error_and_does_not_store_partial_answer` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 92 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 93 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 94 | 환경에 맞게 로드한 설정값을 읽는다. |
| 95 | 가짜로 지정하지 않은 외부 HTTP가 나가지 못하게 막는다. |
| 96 | 지정한 외부 HTTP 응답을 테스트 가짜로 바꾼다. |
| 97 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 98 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 99 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 100 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 101 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 102 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 103 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 104 | `test_mcp_requires_auth_and_hides_foreign_document` 시나리오를 독립된 회귀 테스트로 선언한다. |
| 105 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 106 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 107 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 108 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 109 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 110 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 111 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 112 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 113 | 원문 토큰은 한 번 반환하고 저장소에는 해시와 만료를 기록한다. |
| 114 | 응답·저장 상태·권한·부작용이 시나리오의 기대값과 일치하는지 단언한다. |
| 115 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 116 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


## ④ 🔗 연동 포인트

테스트는 API 계약과 보안의 변경을 배포 전에 멈추는 기준이다. 다음 단계의 배포 점검은 이 테스트와 빌드 결과를 전제로 한다. 심화에서는 같은 테스트를 PostgreSQL·MariaDB 서비스에서도 실행하는 CI 행렬을 사용한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 1. php 명령 없음 | PATH 설정 누락 | 새 터미널에서 경로 확인 |
| 2. No application key | APP_KEY 없음 | 새 로컬 환경에서만 key:generate |
| 3. no such table | DB/마이그레이션 불일치 | migrate:status와 연결 설정 확인 |
| 4. could not find driver | PDO 확장 없음 | php --ini와 php -m 확인 |
| 5. 419 | CSRF·세션 만료 | @csrf와 쿠키 확인 |
| 6. 401 | 토큰 누락·만료 | 로그인/Authorization 확인 |
| 7. 403 | Policy 소유권 거부 | 인증 사용자와 user_id 대조 |
| 8. 404 create | 라우트 순서 오류 | 정적 경로를 먼저 등록 |
| 9. Vite manifest 없음 | 빌드 미실행 | npm ci 후 npm run build |
| 10. 테스트 사용자 혼선 | 같은 테스트에서 가드 캐시 재사용 | 토큰 전환 사이 forgetGuards 호출 |

## ⑥ 직접 해보기

1. TagNames의 trim을 지웠을 때 단위 테스트가 실패하는지 실험 후 복원한다.
2. 다른 계정 삭제 테스트가 DB 행을 보존하는지 단언을 찾는다.
3. AI 실패 가짜 응답을 503으로 지정해 이력이 저장되지 않는지 확인한다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] 단위 테스트와 요청 테스트를 각각 실행했다.
- [ ] DB를 실제로 사용하고 외부 HTTP만 fake로 바꿨다.
- [ ] 오류 TOP 10과 requestId 로그를 확인했다.

## ⑧ 다음 단계 연결

순수 단위 테스트와 DB·HTTP 요청 테스트로 실패 원인을 재현한다. 이 결과를 [study10.md](study10.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://laravel.com/docs/13.x/http-tests)
- [공식 문서 2](https://docs.phpunit.de/en/12.5/)

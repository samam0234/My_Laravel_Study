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

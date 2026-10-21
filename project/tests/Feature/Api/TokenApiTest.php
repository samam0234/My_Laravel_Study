<?php

namespace Tests\Feature\Api;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class TokenApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_token_can_create_a_note_and_is_rejected_after_logout(): void
    {
        $user = User::factory()->create([
            'name' => '미나',
            'email' => 'mina@example.com',
            'password' => 'password123',
        ]);

        $this->postJson('/api/v1/login', [
            'email' => 'mina@example.com',
            'password' => 'nope',
        ])->assertUnprocessable();

        $token = $this->postJson('/api/v1/login', [
            'email' => 'mina@example.com',
            'password' => 'password123',
        ])->assertOk()->json('token');

        $this->postJson('/api/v1/notes', [
            'title' => '토큰 노트',
            'body' => '세션 없음',
            'tags' => 'API',
        ])->assertUnauthorized();

        $this->withToken($token)
            ->postJson('/api/v1/notes', [
                'title' => '토큰 노트',
                'body' => '세션 없음',
                'tags' => 'API, 서재',
            ])
            ->assertCreated()
            ->assertJsonPath('data.author', '미나')
            ->assertJsonPath('data.tags.0', 'API');

        $noteId = $user->notes()->first()->id;

        $this->getJson('/api/v1/notes?tag=서재&per=1')
            ->assertOk()
            ->assertJsonPath('meta.total', 1)
            ->assertJsonPath('data.0.title', '토큰 노트');

        $this->getJson('/api/v1/tags')
            ->assertOk()
            ->assertJsonFragment(['name' => '서재']);

        $other = User::factory()->create();
        $otherToken = $other->createToken('api')->plainTextToken;
        $this->app['auth']->forgetGuards();

        $this->withToken($otherToken)
            ->patchJson("/api/v1/notes/{$noteId}", [
                'title' => '탈취',
                'body' => '안 됨',
                'tags' => '탈취',
            ])
            ->assertForbidden();

        $this->app['auth']->forgetGuards();

        $this->withToken($token)->postJson('/api/v1/logout')->assertNoContent();

        $this->app['auth']->forgetGuards();

        $this->withToken($token)->deleteJson("/api/v1/notes/{$noteId}")->assertUnauthorized();
    }
}

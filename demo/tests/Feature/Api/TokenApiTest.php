<?php

namespace Tests\Feature\Api;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class TokenApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_token_can_create_and_is_rejected_after_logout(): void
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

        $this->postJson('/api/v1/posts', [
            'title' => '토큰으로 쓴 글',
            'body' => '세션 쿠키는 없다',
        ])->assertUnauthorized();

        $this->withToken($token)
            ->postJson('/api/v1/posts', [
                'title' => '토큰으로 쓴 글',
                'body' => '세션 쿠키는 없다',
            ])
            ->assertCreated()
            ->assertJsonPath('data.author', '미나');

        $postId = $user->posts()->first()->id;

        $other = User::factory()->create();
        $otherToken = $other->createToken('api')->plainTextToken;

        $this->app['auth']->forgetGuards();

        $this->withToken($otherToken)
            ->patchJson("/api/v1/posts/{$postId}", [
                'title' => '탈취',
                'body' => '안 됨',
            ])
            ->assertForbidden();

        $this->app['auth']->forgetGuards();

        $this->withToken($token)
            ->postJson("/api/v1/posts/{$postId}/comments", ['body' => '토큰 댓글'])
            ->assertCreated();

        $this->app['auth']->forgetGuards();

        $this->withToken($token)
            ->postJson('/api/v1/logout')
            ->assertNoContent();

        $this->app['auth']->forgetGuards();

        $this->withToken($token)
            ->deleteJson("/api/v1/posts/{$postId}")
            ->assertUnauthorized();

        $this->assertDatabaseHas('posts', ['id' => $postId, 'user_id' => $user->id]);
    }
}

<?php

namespace Tests\Feature\Api;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class CommentApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_comments_are_nested_under_a_post(): void
    {
        $user = User::factory()->create(['name' => '미나']);
        $post = $user->posts()->create(['title' => '글', 'body' => '본문']);
        $other = $user->posts()->create(['title' => '다른 글', 'body' => '본문']);

        $post->comments()->make(['body' => '이 글의 댓글'])->user()->associate($user)->save();
        $other->comments()->make(['body' => '다른 글의 댓글'])->user()->associate($user)->save();

        $this->getJson("/api/v1/posts/{$post->id}/comments")
            ->assertOk()
            ->assertJsonCount(1, 'data')
            ->assertJsonPath('data.0.body', '이 글의 댓글')
            ->assertJsonPath('data.0.author', '미나');

        $this->getJson('/api/v1/posts/999/comments')->assertNotFound();
    }
}

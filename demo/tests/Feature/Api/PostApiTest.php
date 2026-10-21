<?php

namespace Tests\Feature\Api;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class PostApiTest extends TestCase
{
    use RefreshDatabase;

    public function test_posts_are_json_and_newest_first(): void
    {
        $user = User::factory()->create(['name' => '미나']);
        $user->posts()->create(['title' => '먼저', 'body' => '본문 1']);
        $user->posts()->create(['title' => '나중', 'body' => '본문 2']);

        $this->getJson('/api/v1/posts')
            ->assertOk()
            ->assertJsonPath('data.0.title', '나중')
            ->assertJsonPath('data.0.author', '미나')
            ->assertJsonPath('data.1.title', '먼저');
    }

    public function test_one_post_is_a_resource(): void
    {
        $user = User::factory()->create(['name' => '미나']);
        $post = $user->posts()->create(['title' => '한 건', 'body' => '<b>이스케이프는 화면 몫</b>']);

        $this->getJson("/api/v1/posts/{$post->id}")
            ->assertOk()
            ->assertJsonPath('data.body', '<b>이스케이프는 화면 몫</b>')
            ->assertJsonPath('data.author', '미나');

        $this->getJson('/api/v1/posts/999')->assertNotFound();
    }
}

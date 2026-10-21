<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class PostCrudTest extends TestCase
{
    use RefreshDatabase;

    public function test_index_lists_posts(): void
    {
        $user = User::factory()->create(['name' => '미나']);
        $user->posts()->create(['title' => '목록에 보이는 글', 'body' => '본문']);

        $this->get('/posts')
            ->assertOk()
            ->assertSee('목록에 보이는 글')
            ->assertSee('미나');
    }

    public function test_guest_cannot_write(): void
    {
        $this->get('/posts/create')->assertRedirect('/login');
        $this->post('/posts', ['title' => '손님', 'body' => '거절'])->assertRedirect('/login');
    }

    public function test_store_validates_and_creates(): void
    {
        $user = User::factory()->create();

        $this->actingAs($user)
            ->from('/posts/create')
            ->post('/posts', ['title' => '', 'body' => ''])
            ->assertRedirect('/posts/create')
            ->assertSessionHasErrors(['title', 'body']);

        $this->actingAs($user)
            ->post('/posts', ['title' => '저장된 글', 'body' => 'Blade가 다시 그린다'])
            ->assertRedirect('/posts/1');

        $this->assertDatabaseHas('posts', [
            'title' => '저장된 글',
            'user_id' => $user->id,
        ]);
        $this->get('/posts/1')->assertOk()->assertSee('글을 저장했습니다.')->assertSee('저장된 글');
    }

    public function test_only_the_author_can_update_and_delete(): void
    {
        $author = User::factory()->create();
        $post = $author->posts()->create(['title' => '고치기 전', 'body' => '본문']);
        $other = User::factory()->create();

        $this->actingAs($other)
            ->put("/posts/{$post->id}", ['title' => '탈취', 'body' => '안 됨'])
            ->assertForbidden();

        $this->actingAs($author)
            ->put("/posts/{$post->id}", ['title' => '고친 제목', 'body' => '고친 본문'])
            ->assertRedirect("/posts/{$post->id}");

        $this->assertDatabaseHas('posts', ['id' => $post->id, 'title' => '고친 제목']);

        $this->actingAs($author)
            ->delete("/posts/{$post->id}")
            ->assertRedirect('/posts');

        $this->assertDatabaseMissing('posts', ['id' => $post->id]);
    }
}

<?php

namespace Tests\Feature;

use App\Models\Post;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class PostCrudTest extends TestCase
{
    use RefreshDatabase;

    public function test_index_lists_posts(): void
    {
        Post::create(['title' => '목록에 보이는 글', 'body' => '본문']);

        $this->get('/posts')
            ->assertOk()
            ->assertSee('목록에 보이는 글');
    }

    public function test_store_validates_and_creates(): void
    {
        $this->from('/posts/create')
            ->post('/posts', ['title' => '', 'body' => ''])
            ->assertRedirect('/posts/create')
            ->assertSessionHasErrors(['title', 'body']);

        $this->post('/posts', ['title' => '저장된 글', 'body' => 'Blade가 다시 그린다'])
            ->assertRedirect('/posts/1');

        $this->assertDatabaseHas('posts', ['title' => '저장된 글']);
        $this->get('/posts/1')->assertOk()->assertSee('글을 저장했습니다.')->assertSee('저장된 글');
    }

    public function test_update_and_delete(): void
    {
        $post = Post::create(['title' => '고치기 전', 'body' => '본문']);

        $this->put("/posts/{$post->id}", ['title' => '고친 제목', 'body' => '고친 본문'])
            ->assertRedirect("/posts/{$post->id}");

        $this->assertDatabaseHas('posts', ['id' => $post->id, 'title' => '고친 제목']);

        $this->delete("/posts/{$post->id}")
            ->assertRedirect('/posts');

        $this->assertDatabaseMissing('posts', ['id' => $post->id]);
    }
}

<?php

namespace Tests\Feature;

use App\Models\Comment;
use App\Models\Post;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class CommentTest extends TestCase
{
    use RefreshDatabase;

    public function test_a_post_has_many_comments(): void
    {
        $post = Post::create(['title' => '글', 'body' => '본문']);
        $post->comments()->create(['body' => '첫 댓글']);

        $this->assertSame(1, $post->comments()->count());
        $this->assertInstanceOf(Post::class, Comment::first()->post);
    }

    public function test_comment_can_be_stored_and_deleted_on_its_post(): void
    {
        $post = Post::create(['title' => '글', 'body' => '본문']);
        $other = Post::create(['title' => '다른 글', 'body' => '본문']);
        $foreign = $other->comments()->create(['body' => '다른 글의 댓글']);

        $this->post("/posts/{$post->id}/comments", ['body' => '화면에 다는 댓글'])
            ->assertRedirect("/posts/{$post->id}");

        $this->get("/posts/{$post->id}")
            ->assertOk()
            ->assertSee('화면에 다는 댓글');

        $this->get('/posts')->assertSee('댓글 1');

        $this->delete("/posts/{$post->id}/comments/{$foreign->id}")
            ->assertNotFound();

        $comment = $post->comments()->first();
        $this->delete("/posts/{$post->id}/comments/{$comment->id}")
            ->assertRedirect("/posts/{$post->id}");

        $this->assertDatabaseMissing('comments', ['id' => $comment->id]);
    }

    public function test_deleting_a_post_deletes_its_comments(): void
    {
        $post = Post::create(['title' => '글', 'body' => '본문']);
        $comment = $post->comments()->create(['body' => '같이 지워질 댓글']);

        $post->delete();

        $this->assertDatabaseMissing('comments', ['id' => $comment->id]);
    }
}

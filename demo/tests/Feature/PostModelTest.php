<?php

namespace Tests\Feature;

use App\Models\Post;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class PostModelTest extends TestCase
{
    use RefreshDatabase;

    public function test_a_post_row_is_a_model(): void
    {
        $post = Post::create([
            'title' => '첫 마이그레이션',
            'body' => '스키마는 모델 파일이 아니라 마이그레이션에 있다.',
        ]);

        $this->assertDatabaseHas('posts', [
            'id' => $post->id,
            'title' => '첫 마이그레이션',
        ]);
        $this->assertSame('Asia/Seoul', $post->created_at->timezoneName);
    }

    public function test_columns_outside_fillable_are_ignored(): void
    {
        $post = Post::create([
            'title' => '채울 수 있는 컬럼만',
            'body' => 'id는 fillable이 아니다.',
            'id' => 99,
        ]);

        $this->assertNotSame(99, $post->id);
    }
}

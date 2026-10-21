<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class ShelfTest extends TestCase
{
    use RefreshDatabase;

    public function test_index_filters_by_search_and_tag(): void
    {
        $user = User::factory()->create(['name' => '미나']);
        $first = $user->notes()->create(['title' => '스키마 노트', 'body' => '마이그레이션']);
        $first->syncTagString('Eloquent');
        $user->notes()->create(['title' => '화면 노트', 'body' => 'Blade'])->syncTagString('Blade');

        $this->get('/notes?q=스키마')
            ->assertOk()
            ->assertSee('스키마 노트')
            ->assertDontSee('화면 노트');

        $this->get('/notes?tag=Blade')
            ->assertOk()
            ->assertSee('화면 노트')
            ->assertDontSee('스키마 노트');
    }

    public function test_guest_cannot_write_and_author_can_store_tags(): void
    {
        $this->get('/notes/create')->assertRedirect('/login');

        $user = User::factory()->create();
        $this->actingAs($user)
            ->post('/notes', [
                'title' => '저장한 노트',
                'body' => '태그까지',
                'tags' => 'Eloquent, 서재',
            ])
            ->assertRedirect('/notes/1');

        $this->get('/notes/1')
            ->assertOk()
            ->assertSee('노트를 저장했습니다.')
            ->assertSee('Eloquent')
            ->assertSee('서재');
    }

    public function test_only_the_author_can_update(): void
    {
        $author = User::factory()->create();
        $note = $author->notes()->create(['title' => '고치기 전', 'body' => '본문']);
        $note->syncTagString('초안');
        $other = User::factory()->create();

        $this->actingAs($other)
            ->put("/notes/{$note->id}", ['title' => '탈취', 'body' => '안 됨', 'tags' => '탈취'])
            ->assertForbidden();

        $this->actingAs($author)
            ->put("/notes/{$note->id}", ['title' => '고친 제목', 'body' => '고친 본문', 'tags' => '수정'])
            ->assertRedirect("/notes/{$note->id}");

        $this->assertDatabaseHas('notes', ['id' => $note->id, 'title' => '고친 제목']);
        $this->assertSame(['수정'], $note->fresh()->tags->pluck('name')->all());
    }
}

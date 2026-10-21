<?php

namespace Tests\Feature;

use App\Models\Note;
use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class NoteModelTest extends TestCase
{
    use RefreshDatabase;

    public function test_tags_are_many_to_many_and_user_id_is_not_fillable(): void
    {
        $user = User::factory()->create();
        $note = $user->notes()->create([
            'title' => '관계',
            'body' => '본문',
            'user_id' => 999,
        ]);
        $note->syncTagString('Eloquent, 스키마, Eloquent');

        $this->assertSame($user->id, $note->fresh()->user_id);
        $this->assertSame(['Eloquent', '스키마'], $note->tags()->orderBy('name')->pluck('name')->all());

        $ignored = Note::query()->create([
            'title' => '직접',
            'body' => '채우기 거부',
            'user_id' => $user->id,
        ]);
        $this->assertNull($ignored->user_id);

        $note->delete();
        $this->assertDatabaseMissing('note_tag', ['note_id' => $note->id]);
        $this->assertDatabaseHas('tags', ['name' => 'Eloquent']);
    }
}

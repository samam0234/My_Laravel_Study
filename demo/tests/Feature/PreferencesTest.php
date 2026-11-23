<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Storage;
use Tests\TestCase;

class PreferencesTest extends TestCase
{
    use RefreshDatabase;

    public function test_preferences_are_saved_in_the_owners_private_file_and_session(): void
    {
        $user = User::factory()->create();
        Storage::fake('local');

        $this->actingAs($user)->post('/study/preferences', ['theme' => 'dark', 'user_id' => 999])
            ->assertRedirect('/study/preferences')->assertSessionHas('theme', 'dark');

        Storage::disk('local')->assertExists('preferences/'.$user->id.'.json');
        Storage::disk('local')->assertMissing('preferences/999.json');
        $this->get('/study/preferences')->assertOk()->assertViewHas('theme', 'dark');
    }

    public function test_invalid_theme_returns_errors_without_writing_a_file(): void
    {
        $user = User::factory()->create();
        Storage::fake('local');

        $this->actingAs($user)->post('/study/preferences', ['theme' => '<script>'])
            ->assertSessionHasErrors('theme');

        Storage::disk('local')->assertMissing('preferences/'.$user->id.'.json');
    }
}

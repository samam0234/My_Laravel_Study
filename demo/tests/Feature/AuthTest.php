<?php

namespace Tests\Feature;

use App\Models\User;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Hash;
use Tests\TestCase;

class AuthTest extends TestCase
{
    use RefreshDatabase;

    public function test_register_starts_a_session(): void
    {
        $this->post('/register', [
            'name' => '새 회원',
            'email' => 'new@example.com',
            'password' => 'password123',
            'password_confirmation' => 'password123',
        ])->assertRedirect('/posts');

        $user = User::where('email', 'new@example.com')->first();
        $this->assertNotNull($user);
        $this->assertTrue(Hash::check('password123', $user->password));
        $this->assertAuthenticatedAs($user);
    }

    public function test_login_and_logout(): void
    {
        $user = User::factory()->create([
            'email' => 'mina@example.com',
            'password' => 'password123',
        ]);

        $this->post('/login', [
            'email' => 'mina@example.com',
            'password' => 'wrong-password',
        ])->assertSessionHasErrors('email');

        $this->post('/login', [
            'email' => 'mina@example.com',
            'password' => 'password123',
        ])->assertRedirect('/posts');

        $this->assertAuthenticatedAs($user);

        $this->post('/logout')->assertRedirect('/');
        $this->assertGuest();
    }
}

<?php

namespace Tests\Feature;

use App\Models\User;
use App\Notifications\DocumentReady;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Support\Facades\Http;
use Laravel\Socialite\Facades\Socialite;
use Laravel\Socialite\Two\User as SocialUser;
use Tests\TestCase;

class IntegrationTest extends TestCase
{
    use RefreshDatabase;

    public function test_signed_webhook_is_idempotent_and_bad_signature_returns_400(): void
    {
        config(['services.stripe.webhook_secret' => 'test-secret']);
        $body = json_encode(['id' => 'evt_test', 'type' => 'checkout.session.completed']);
        $timestamp = (string) time();
        $signature = hash_hmac('sha256', $timestamp.'.'.$body, 'test-secret');
        $headers = ['CONTENT_TYPE' => 'application/json', 'HTTP_ACCEPT' => 'application/json', 'HTTP_STRIPE_SIGNATURE' => 't='.$timestamp.',v1='.$signature];
        $this->call('POST', '/api/webhooks/stripe', [], [], [], $headers, $body)->assertOk()->assertJsonPath('data.duplicate', false);
        $this->call('POST', '/api/webhooks/stripe', [], [], [], $headers, $body)->assertOk()->assertJsonPath('data.duplicate', true);
        $headers['HTTP_STRIPE_SIGNATURE'] = 't='.$timestamp.',v1=invalid';
        $this->call('POST', '/api/webhooks/stripe', [], [], [], $headers, $body)->assertBadRequest();
        $this->assertDatabaseCount('integration_receipts', 1);
    }

    public function test_checkout_uses_server_price_instead_of_client_price(): void
    {
        $user = User::factory()->create();
        config(['services.stripe.secret' => 'sk_test', 'services.stripe.price' => 'price_server']);
        Http::preventStrayRequests();
        Http::fake(['https://api.stripe.com/v1/checkout/sessions' => Http::response(['url' => 'https://checkout.stripe.com/test'], 200)]);
        $this->withToken($user->createToken('test')->plainTextToken)->postJson('/api/checkout', ['price' => 'price_attacker'])->assertOk()->assertJsonPath('data.url', 'https://checkout.stripe.com/test');
        Http::assertSent(fn ($request) => $request['line_items[0][price]'] === 'price_server'
            && $request['success_url'] === rtrim(config('app.url'), '/').'/app?checkout=success');
    }

    public function test_oauth_creates_provider_account_and_regenerates_session(): void
    {
        $identity = (new SocialUser)->map(['id' => 'github-123', 'name' => '학습자', 'email' => 'oauth@example.com']);
        Socialite::shouldReceive('driver')->with('github')->andReturnSelf();
        Socialite::shouldReceive('user')->once()->andReturn($identity);
        $this->get('/auth/github/callback')->assertRedirect('/notes');
        $this->assertAuthenticated();
        $this->assertDatabaseHas('users', ['github_id' => 'github-123', 'email' => 'oauth@example.com']);
    }

    public function test_oauth_never_links_an_existing_email_automatically(): void
    {
        User::factory()->create(['email' => 'existing@example.com']);
        $identity = (new SocialUser)->map(['id' => 'attacker', 'email' => 'existing@example.com']);
        Socialite::shouldReceive('driver')->with('github')->andReturnSelf();
        Socialite::shouldReceive('user')->once()->andReturn($identity);
        $this->get('/auth/github/callback')->assertConflict();
        $this->assertGuest();
        $this->assertDatabaseCount('users', 1);
    }

    public function test_notification_is_persisted_and_mail_renders_without_document_content(): void
    {
        $user = User::factory()->create();
        config(['broadcasting.default' => 'null']);
        $user->notify(new DocumentReady(123));
        $this->assertDatabaseCount('notifications', 1);
        $mail = (new DocumentReady(123))->toMail($user)->render();
        $this->assertStringContainsString('/app', (string) $mail);
    }

    public function test_private_broadcast_channel_auth_rejects_another_users_channel(): void
    {
        $user = User::factory()->create();
        config(['broadcasting.default' => 'reverb', 'broadcasting.connections.reverb.key' => 'study', 'broadcasting.connections.reverb.secret' => 'study-secret', 'broadcasting.connections.reverb.app_id' => 'study']);
        require base_path('routes/channels.php');
        $this->withToken($user->createToken('websocket')->plainTextToken)->postJson('/api/broadcasting/auth', ['socket_id' => '123.456', 'channel_name' => 'private-App.Models.User.'.$user->id])->assertOk()->assertJsonStructure(['auth']);
        $this->postJson('/api/broadcasting/auth', ['socket_id' => '123.456', 'channel_name' => 'private-App.Models.User.999'])->assertForbidden();
    }
}

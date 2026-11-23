<?php

namespace App\Http\Controllers;

use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\RedirectResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Str;
use Laravel\Socialite\Facades\Socialite;
use Symfony\Component\HttpFoundation\RedirectResponse as OAuthRedirect;
use Throwable;

class IntegrationController extends Controller
{
    public function redirect(): OAuthRedirect
    {
        abort_unless(config('services.github.client_id'), 503);

        return Socialite::driver('github')->scopes(['user:email'])->redirect();
    }

    public function callback(Request $request): RedirectResponse
    {
        abort_if($request->has('error'), 400, 'OAuth denied');
        try {
            $identity = Socialite::driver('github')->user();
        } catch (Throwable $exception) {
            report($exception);
            abort(400, 'OAuth state or provider failed');
        }
        abort_unless($identity->getEmail(), 422, '공개 이메일을 설정하세요.');
        $user = User::query()->where('github_id', $identity->getId())->first();
        if (! $user) {
            abort_if(User::query()->where('email', $identity->getEmail())->exists(), 409, '기존 계정은 자동 연결하지 않습니다.');
            $user = new User(['name' => $identity->getName() ?: $identity->getNickname(), 'email' => $identity->getEmail(), 'password' => Str::random(64)]);
            $user->github_id = $identity->getId();
            $user->save();
        }
        Auth::login($user);
        $request->session()->regenerate();

        return redirect()->route('notes.index');
    }

    public function checkout(Request $request): JsonResponse
    {
        abort_unless(config('services.stripe.secret') && config('services.stripe.price'), 503);
        $session = Http::asForm()->withToken(config('services.stripe.secret'))->connectTimeout(5)->timeout(20)
            ->withHeaders(['Idempotency-Key' => $request->user()->id.'-'.now()->format('YmdHi')])
            ->post('https://api.stripe.com/v1/checkout/sessions', [
                'mode' => 'payment', 'line_items[0][price]' => config('services.stripe.price'), 'line_items[0][quantity]' => 1,
                'client_reference_id' => (string) $request->user()->id,
                'success_url' => rtrim(config('app.url'), '/').'/app?checkout=success',
                'cancel_url' => rtrim(config('app.url'), '/').'/app?checkout=cancel',
            ]);
        abort_unless($session->successful(), 502);

        return response()->json(['data' => ['url' => $session->json('url')]]);
    }

    public function webhook(Request $request): JsonResponse
    {
        $secret = config('services.stripe.webhook_secret');
        abort_unless($secret, 503);
        $parts = [];
        foreach (explode(',', $request->header('Stripe-Signature', '')) as $piece) {
            $pair = explode('=', $piece, 2);
            if (count($pair) === 2) {
                $parts[$pair[0]][] = $pair[1];
            }
        }
        $timestamp = $parts['t'][0] ?? '';
        abort_unless(ctype_digit($timestamp) && abs(time() - (int) $timestamp) <= 300, 400);
        $expected = hash_hmac('sha256', $timestamp.'.'.$request->getContent(), $secret);
        $valid = false;
        foreach ($parts['v1'] ?? [] as $signature) {
            $valid = hash_equals($expected, $signature) || $valid;
        }
        abort_unless($valid, 400);
        $data = $request->validate(['id' => ['required', 'string', 'max:255'], 'type' => ['required', 'string', 'max:255']]);
        $inserted = DB::table('integration_receipts')->insertOrIgnore(['event_id' => $data['id'], 'type' => $data['type'], 'created_at' => now(), 'updated_at' => now()]);

        return response()->json(['data' => ['received' => true, 'duplicate' => $inserted === 0]]);
    }
}

<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\User;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Hash;
use Symfony\Component\HttpFoundation\Response;

class AuthController extends Controller
{
    public function signup(Request $request): JsonResponse
    {
        $data = $request->validate([
            'nickname' => ['required', 'string', 'max:80'],
            'email' => ['required', 'email', 'max:255'],
            'password' => ['required', 'string', 'min:12', 'max:128'],
        ]);
        abort_if(User::query()->where('email', $data['email'])->exists(), 409, 'EMAIL_TAKEN');
        $user = User::query()->create(['name' => $data['nickname'], 'email' => $data['email'], 'password' => $data['password']]);

        return $this->token($user, 201);
    }

    public function login(Request $request): JsonResponse
    {
        $data = $request->validate(['email' => ['required', 'email'], 'password' => ['required', 'string']]);
        $user = User::query()->where('email', $data['email'])->first();
        abort_unless($user && Hash::check($data['password'], $user->password), 401, 'INVALID_CREDENTIALS');

        return $this->token($user);
    }

    public function me(Request $request): JsonResponse
    {
        $user = $request->user();

        return response()->json(['data' => ['id' => $user->id, 'email' => $user->email, 'nickname' => $user->name]]);
    }

    public function logout(Request $request): Response
    {
        $request->user()->currentAccessToken()?->delete();

        return response()->noContent();
    }

    private function token(User $user, int $status = 200): JsonResponse
    {
        return response()->json(['data' => [
            'user' => ['id' => $user->id, 'email' => $user->email, 'nickname' => $user->name],
            'accessToken' => $user->createToken('vue', ['*'], now()->addHour())->plainTextToken,
        ]], $status);
    }
}

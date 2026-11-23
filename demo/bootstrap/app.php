<?php

use App\Http\Middleware\RequestContext;
use Illuminate\Foundation\Application;
use Illuminate\Foundation\Configuration\Exceptions;
use Illuminate\Foundation\Configuration\Middleware;
use Illuminate\Http\Request;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\Response;

return Application::configure(basePath: dirname(__DIR__))
    ->withRouting(
        web: __DIR__.'/../routes/web.php',
        api: __DIR__.'/../routes/api.php',
        commands: __DIR__.'/../routes/console.php',
        health: '/up',
    )
    ->withMiddleware(function (Middleware $middleware): void {
        $middleware->prepend(RequestContext::class);
    })
    ->withExceptions(function (Exceptions $exceptions): void {
        $exceptions->shouldRenderJsonWhen(fn (Request $request) => $request->is('api/*') || $request->expectsJson());
        $exceptions->respond(function (Response $response): Response {
            $request = request();
            if (! $request->is('api/*') || $request->is('api/v1/*') || $response->getStatusCode() < 400) {
                return $response;
            }
            $status = $response->getStatusCode();
            $payload = json_decode($response->getContent(), true) ?? [];
            $fields = $payload['errors'] ?? (object) [];
            $message = $payload['message'] ?? '';
            $code = match ($status) {
                422 => 'VALIDATION_ERROR', 400 => 'BAD_REQUEST',
                401 => $message === 'INVALID_CREDENTIALS' ? 'INVALID_CREDENTIALS' : 'UNAUTHORIZED',
                403 => 'FORBIDDEN', 404 => 'NOT_FOUND', 409 => 'EMAIL_TAKEN',
                413 => 'PAYLOAD_TOO_LARGE', 429 => 'RATE_LIMITED',
                502 => 'UPSTREAM_ERROR', 503 => 'SERVICE_UNAVAILABLE', default => 'INTERNAL',
            };
            $status = $status === 422 ? 400 : $status;
            $id = $request->attributes->get('requestId', (string) Str::uuid());
            $result = response()->json(['error' => [
                'code' => $code, 'message' => $status >= 500 ? '서비스 연결을 확인해 주세요.' : '요청을 확인해 주세요.',
                'fields' => $fields, 'requestId' => $id,
            ]], $status)->header('X-Request-Id', $id)->header('Content-Type', 'application/json; charset=utf-8');
            foreach (['Retry-After', 'WWW-Authenticate', 'Allow'] as $header) {
                if ($response->headers->has($header)) {
                    $result->headers->set($header, $response->headers->get($header));
                }
            }

            return $result;
        });
    })->create();

<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Str;
use Symfony\Component\HttpFoundation\Response;

class RequestContext
{
    public function handle(Request $request, Closure $next): Response
    {
        $id = $request->header('X-Request-Id');
        $id = is_string($id) && preg_match('/^[a-zA-Z0-9-]{1,80}$/', $id) ? $id : (string) Str::uuid();
        $request->attributes->set('requestId', $id);
        Log::withContext(['requestId' => $id]);
        if ($request->is('api/*') && ! $request->is('api/v1/*') && $request->isJson() && $request->getContent() !== '') {
            try {
                $json = json_decode($request->getContent(), true, 512, JSON_THROW_ON_ERROR);
                abort_unless(is_array($json), 400, 'BAD_REQUEST');
            } catch (\JsonException) {
                abort(400, 'BAD_REQUEST');
            }
        }
        $response = $next($request);
        $response->headers->set('X-Request-Id', $id);
        if (str_starts_with($response->headers->get('Content-Type', ''), 'application/json')) {
            $response->headers->set('Content-Type', 'application/json; charset=utf-8');
        }

        return $response;
    }
}

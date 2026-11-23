<?php

use App\Http\Controllers\Api\V1\NoteController;
use App\Http\Controllers\Api\V1\TagController;
use App\Http\Controllers\Api\V1\TokenController;
use Illuminate\Support\Facades\Route;

Route::prefix('v1')->group(function () {
    Route::post('/login', [TokenController::class, 'store']);
    Route::get('/notes', [NoteController::class, 'index']);
    Route::get('/notes/{note}', [NoteController::class, 'show']);
    Route::get('/tags', [TagController::class, 'index']);

    Route::middleware('auth:sanctum')->group(function () {
        Route::post('/logout', [TokenController::class, 'destroy']);
        Route::post('/notes', [NoteController::class, 'store']);
        Route::match(['put', 'patch'], '/notes/{note}', [NoteController::class, 'update']);
        Route::delete('/notes/{note}', [NoteController::class, 'destroy']);
    });
});

use App\Http\Controllers\Api\AuthController as ContractAuth;
use App\Http\Controllers\Api\CommentContractController;
use App\Http\Controllers\Api\ContractController;
use App\Http\Controllers\Api\DocumentController;
use App\Http\Controllers\IntegrationController;
use App\Services\LibraryStats;
use Illuminate\Http\Request;

Route::post('/auth/signup', [ContractAuth::class, 'signup'])->middleware('throttle:10,1');
Route::post('/auth/login', [ContractAuth::class, 'login'])->middleware('throttle:10,1');
Route::get('/posts', [ContractController::class, 'index']);
Route::get('/posts/{id}', [ContractController::class, 'show'])->whereNumber('id');
Route::middleware('auth:sanctum')->group(function () {
    Route::get('/auth/me', [ContractAuth::class, 'me']);
    Route::post('/auth/logout', [ContractAuth::class, 'logout']);
    Route::post('/posts', [ContractController::class, 'store']);
    Route::patch('/posts/{id}', [ContractController::class, 'update'])->whereNumber('id');
    Route::delete('/posts/{id}', [ContractController::class, 'destroy'])->whereNumber('id');
});

Route::post('/webhooks/stripe', [IntegrationController::class, 'webhook']);
Route::middleware(['auth:sanctum', 'throttle:30,1'])->group(function () {
    Route::get('/documents', [DocumentController::class, 'index']);
    Route::post('/documents', [DocumentController::class, 'store']);
    Route::get('/documents/{document}/download', [DocumentController::class, 'download']);
    Route::delete('/documents/{document}', [DocumentController::class, 'destroy']);
    Route::get('/documents/{document}/questions', [DocumentController::class, 'history']);
    Route::post('/documents/{document}/ask', [DocumentController::class, 'ask'])->middleware('throttle:6,1');
    Route::get('/notifications', fn (Request $request) => response()->json(['data' => $request->user()->notifications()->latest()->limit(20)->get()->map(fn ($item) => [
        'id' => $item->id, 'data' => $item->data, 'readAt' => $item->read_at?->utc()->toISOString(), 'createdAt' => $item->created_at?->utc()->toISOString(),
    ])]));
    Route::post('/checkout', [IntegrationController::class, 'checkout']);
});

Route::get('/posts/{post}/comments', [CommentContractController::class, 'index'])->whereNumber('post');
Route::post('/posts/{post}/comments', [CommentContractController::class, 'store'])->middleware('auth:sanctum')->whereNumber('post');
Route::delete('/comments/{comment}', [CommentContractController::class, 'destroy'])->middleware('auth:sanctum')->whereNumber('comment');

Route::get('/posts/{invalid}', fn () => abort(400))->where('invalid', '[^0-9/]+');

Route::get('/stats', fn (LibraryStats $stats) => response()->json(['data' => ['total' => $stats->total()]]));

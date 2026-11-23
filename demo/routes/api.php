<?php

use App\Http\Controllers\Api\V1\CommentController;
use App\Http\Controllers\Api\V1\PostController;
use App\Http\Controllers\Api\V1\TokenController;
use Illuminate\Support\Facades\Route;

Route::prefix('v1')->group(function () {
    Route::post('/login', [TokenController::class, 'store']);

    Route::get('/posts', [PostController::class, 'index']);
    Route::get('/posts/{post}', [PostController::class, 'show']);
    Route::get('/posts/{post}/comments', [CommentController::class, 'index']);

    Route::middleware('auth:sanctum')->group(function () {
        Route::post('/logout', [TokenController::class, 'destroy']);
        Route::post('/posts', [PostController::class, 'store']);
        Route::match(['put', 'patch'], '/posts/{post}', [PostController::class, 'update']);
        Route::delete('/posts/{post}', [PostController::class, 'destroy']);
        Route::post('/posts/{post}/comments', [CommentController::class, 'store']);
        Route::delete('/posts/{post}/comments/{comment}', [CommentController::class, 'destroy'])
            ->scopeBindings();
    });
});

use App\Http\Controllers\Api\AuthController as ContractAuth;
use App\Http\Controllers\Api\CommentContractController;
use App\Http\Controllers\Api\ContractController;
use App\Services\LibraryStats;

Route::get('/posts/{post}/comments', [CommentContractController::class, 'index'])->whereNumber('post');
Route::post('/posts/{post}/comments', [CommentContractController::class, 'store'])->middleware('auth:sanctum')->whereNumber('post');
Route::delete('/comments/{comment}', [CommentContractController::class, 'destroy'])->middleware('auth:sanctum')->whereNumber('comment');
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

Route::get('/posts/{invalid}', fn () => abort(400))->where('invalid', '[^0-9/]+');

Route::get('/stats', fn (LibraryStats $stats) => response()->json(['data' => ['total' => $stats->total()]]));

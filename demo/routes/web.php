<?php

use App\Http\Controllers\Auth\RegisteredUserController;
use App\Http\Controllers\Auth\SessionController;
use App\Http\Controllers\CommentController;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\LearningController;
use App\Http\Controllers\PostController;
use Illuminate\Support\Facades\Route;

Route::get('/', [HomeController::class, 'index'])->name('home');

Route::middleware('guest')->group(function () {
    Route::get('/register', [RegisteredUserController::class, 'create'])->name('register');
    Route::post('/register', [RegisteredUserController::class, 'store']);
    Route::get('/login', [SessionController::class, 'create'])->name('login');
    Route::post('/login', [SessionController::class, 'store'])->middleware('throttle:10,1');
});

Route::post('/logout', [SessionController::class, 'destroy'])
    ->middleware('auth')
    ->name('logout');

Route::middleware('auth')->group(function () {
    Route::resource('posts', PostController::class)->except(['index', 'show']);
    Route::post('/posts/{post}/comments', [CommentController::class, 'store'])
        ->name('posts.comments.store');
    Route::delete('/posts/{post}/comments/{comment}', [CommentController::class, 'destroy'])
        ->scopeBindings()
        ->name('posts.comments.destroy');
});

Route::resource('posts', PostController::class)->only(['index', 'show']);

Route::view('/app', 'workspace')->name('workspace');
Route::get('/health', fn () => response()->json(['status' => 'ok']));

Route::view('/api-docs', 'api-docs');
Route::get('/study/preferences', [LearningController::class, 'preferences'])->middleware('auth')->name('study.preferences');
Route::post('/study/preferences', [LearningController::class, 'save'])->middleware('auth')->name('study.preferences.save');

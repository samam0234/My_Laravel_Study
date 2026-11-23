<?php

use App\Http\Controllers\Auth\RegisteredUserController;
use App\Http\Controllers\Auth\SessionController;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\IntegrationController;
use App\Http\Controllers\NoteController;
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
    Route::resource('notes', NoteController::class)->except(['index', 'show']);
});

Route::resource('notes', NoteController::class)->only(['index', 'show']);

Route::view('/app', 'workspace')->name('workspace');
Route::get('/health', fn () => response()->json(['status' => 'ok']));

Route::get('/auth/github', [IntegrationController::class, 'redirect'])->middleware('guest');
Route::get('/auth/github/callback', [IntegrationController::class, 'callback'])->middleware('guest');

Route::view('/api-docs', 'api-docs');

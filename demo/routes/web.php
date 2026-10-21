<?php

use App\Http\Controllers\CommentController;
use App\Http\Controllers\HomeController;
use App\Http\Controllers\PostController;
use Illuminate\Support\Facades\Route;

Route::get('/', [HomeController::class, 'index'])->name('home');
Route::resource('posts', PostController::class);
Route::post('/posts/{post}/comments', [CommentController::class, 'store'])
    ->name('posts.comments.store');
Route::delete('/posts/{post}/comments/{comment}', [CommentController::class, 'destroy'])
    ->scopeBindings()
    ->name('posts.comments.destroy');

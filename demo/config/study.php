<?php

use App\Models\Post;

return [
    'model' => Post::class,
    'relation' => 'posts',
    'ai_driver' => env('AI_DRIVER', 'mock'),
    'ai_url' => env('AI_URL', 'http://127.0.0.1:11434'),
    'ai_model' => env('AI_Post', 'gemma4:12b'),
];

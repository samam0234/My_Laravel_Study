<?php

use App\Models\Note;

return [
    'model' => Note::class,
    'relation' => 'notes',
    'ai_driver' => env('AI_DRIVER', 'mock'),
    'ai_url' => env('AI_URL', 'http://127.0.0.1:11434'),
    'ai_model' => env('AI_Note', 'gemma4:12b'),
];

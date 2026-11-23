<?php

namespace Database\Factories;

use App\Models\User;
use Illuminate\Database\Eloquent\Factories\Factory;

class DocumentFactory extends Factory
{
    public function definition(): array
    {
        return ['user_id' => User::factory(), 'filename' => 'study.txt', 'path' => 'documents/study.txt',
            'content' => 'Laravel 문서의 핵심은 인증과 소유권입니다.', 'status' => 'queued'];
    }
}

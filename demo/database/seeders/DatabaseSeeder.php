<?php

namespace Database\Seeders;

use App\Models\Post;
use App\Models\User;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    /**
     * Seed the application's database.
     */
    public function run(): void
    {
        // User::factory(10)->create();

        User::factory()->create([
            'name' => 'Test User',
            'email' => 'test@example.com',
        ]);

        Post::create([
            'title' => 'Eloquent는 한 줄이 객체다',
            'body' => 'Post::create는 INSERT입니다. 스키마는 마이그레이션에 있습니다.',
        ]);
        Post::create([
            'title' => 'Blade는 다음 실습에서 붙인다',
            'body' => '지금은 테이블과 모델만 확인합니다.',
        ]);
    }
}

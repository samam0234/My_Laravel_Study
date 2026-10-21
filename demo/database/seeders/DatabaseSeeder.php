<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Console\Seeds\WithoutModelEvents;
use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    use WithoutModelEvents;

    public function run(): void
    {
        $mina = User::factory()->create([
            'name' => '미나',
            'email' => 'mina@example.com',
            'password' => 'password123',
        ]);

        $first = $mina->posts()->create([
            'title' => 'Eloquent는 한 줄이 객체다',
            'body' => 'Post::create는 INSERT입니다. 스키마는 마이그레이션에 있습니다.',
        ]);
        $first->comments()->make([
            'body' => '관계로 저장하면 post_id가 채워집니다.',
        ])->user()->associate($mina)->save();

        $mina->posts()->create([
            'title' => '세션 로그인은 쿠키다',
            'body' => 'API 토큰은 study9에서 Sanctum으로 분리합니다.',
        ]);
    }
}

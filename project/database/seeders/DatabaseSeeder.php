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

        $schema = $mina->notes()->create([
            'title' => '마이그레이션은 스키마의 기록이다',
            'body' => '노트와 태그는 다대다입니다. 게시판의 댓글 관계와는 테이블이 다릅니다.',
        ]);
        $schema->syncTagString('Eloquent, 스키마');

        $blade = $mina->notes()->create([
            'title' => 'Blade는 서버가 그린다',
            'body' => '이 화면은 세션 쿠키를 씁니다. 다른 포트의 화면은 Sanctum 토큰을 씁니다.',
        ]);
        $blade->syncTagString('Blade');
    }
}

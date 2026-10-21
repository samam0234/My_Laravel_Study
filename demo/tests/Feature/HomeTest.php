<?php

namespace Tests\Feature;

use Tests\TestCase;

class HomeTest extends TestCase
{
    public function test_home_renders_the_blade_intro(): void
    {
        $this->get('/')
            ->assertOk()
            ->assertSee('Laravel 게시판을 이 폴더에서 만듭니다.')
            ->assertSee('/up', false);
    }

    public function test_health_check_is_ok(): void
    {
        $this->get('/up')->assertOk();
    }
}

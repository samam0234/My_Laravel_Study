<?php

namespace Tests\Feature\Api;

use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class CorsTest extends TestCase
{
    use RefreshDatabase;

    public function test_the_project_js_origin_is_allowed(): void
    {
        $this->withHeader('Origin', 'http://127.0.0.1:5180')
            ->getJson('/api/v1/notes')
            ->assertOk()
            ->assertHeader('Access-Control-Allow-Origin', 'http://127.0.0.1:5180');
    }

    public function test_a_random_origin_is_not_echoed(): void
    {
        $response = $this->withHeader('Origin', 'http://evil.example')
            ->getJson('/api/v1/notes');

        $response->assertOk();
        $this->assertNotSame('http://evil.example', $response->headers->get('Access-Control-Allow-Origin'));
    }
}

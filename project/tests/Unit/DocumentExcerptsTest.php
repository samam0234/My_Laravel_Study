<?php

namespace Tests\Unit;

use App\Services\DocumentAi;
use PHPUnit\Framework\TestCase;

class DocumentExcerptsTest extends TestCase
{
    public function test_retrieval_selects_relevant_chunks_and_preserves_source_number(): void
    {
        $content = str_repeat('a', 1000).' Laravel 인증은 사용자의 소유권을 확인합니다.';
        $sources = (new DocumentAi)->excerpts($content, 'Laravel 소유권');

        $this->assertSame(2, $sources[0]['index']);
        $this->assertStringContainsString('소유권', $sources[0]['text']);
    }

    public function test_retrieval_returns_no_sources_for_unrelated_question(): void
    {
        $this->assertSame([], (new DocumentAi)->excerpts('Laravel 인증 문서', '천문학 블랙홀'));
    }
}

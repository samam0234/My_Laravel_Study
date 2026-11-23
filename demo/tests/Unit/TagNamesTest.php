<?php

namespace Tests\Unit;

use App\Support\TagNames;
use PHPUnit\Framework\TestCase;

class TagNamesTest extends TestCase
{
    public function test_normalization_trims_deduplicates_and_keeps_string_zero(): void
    {
        $this->assertSame(['Laravel', '0'], TagNames::normalize([' Laravel ', '', 'Laravel', '0']));
    }

    public function test_normalization_limits_unicode_length_and_number_of_tags(): void
    {
        $names = [str_repeat('한', 40), ...array_map(fn ($n) => '태그'.$n, range(1, 10))];
        $actual = TagNames::normalize($names);
        $this->assertCount(8, $actual);
        $this->assertSame(str_repeat('한', 30), $actual[0]);
    }
}

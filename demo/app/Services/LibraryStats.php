<?php

namespace App\Services;

use Illuminate\Support\Facades\Cache;

class LibraryStats
{
    public function total(): int
    {
        return Cache::remember('study.total', 30, fn () => config('study.model')::query()->count());
    }

    public function invalidate(): void
    {
        Cache::forget('study.total');
    }
}

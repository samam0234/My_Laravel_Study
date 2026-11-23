<?php

namespace App\Support;

class TagNames
{
    public static function normalize(array $names): array
    {
        $names = array_map(fn (string $name): string => mb_substr(trim($name), 0, 30), $names);

        return array_slice(array_values(array_unique(array_filter($names, fn ($name) => $name !== ''))), 0, 8);
    }
}

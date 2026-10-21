<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Models\Tag;

class TagController extends Controller
{
    public function index()
    {
        $tags = Tag::query()->withCount('notes')->orderBy('name')->get();

        return response()->json([
            'data' => $tags->map(fn (Tag $tag) => [
                'id' => $tag->id,
                'name' => $tag->name,
                'notes_count' => $tag->notes_count,
            ])->values(),
        ]);
    }
}

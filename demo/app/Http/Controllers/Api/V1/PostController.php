<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Resources\PostResource;
use App\Models\Post;
use Illuminate\Http\Request;

class PostController extends Controller
{
    public function index(Request $request)
    {
        $this->authorize('viewAny', Post::class);

        $perPage = min(max($request->integer('per', 10), 1), 50);
        $posts = Post::query()
            ->with('user')
            ->search($request->query('q'))
            ->latest('id')
            ->paginate($perPage)
            ->withQueryString();

        return PostResource::collection($posts);
    }

    public function show(Post $post)
    {
        $this->authorize('view', $post);
        $post->load('user');

        return new PostResource($post);
    }
}

<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Resources\PostResource;
use App\Models\Post;

class PostController extends Controller
{
    public function index()
    {
        $posts = Post::query()->with('user')->latest('id')->get();

        return PostResource::collection($posts);
    }

    public function show(Post $post)
    {
        $post->load('user');

        return new PostResource($post);
    }
}

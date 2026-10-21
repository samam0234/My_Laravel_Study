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

    public function store(Request $request)
    {
        $data = $this->validated($request);
        $post = $request->user()->posts()->create($data);

        return (new PostResource($post->load('user')))
            ->response()
            ->setStatusCode(201);
    }

    public function show(Post $post)
    {
        $this->authorize('view', $post);
        $post->load('user');

        return new PostResource($post);
    }

    public function update(Request $request, Post $post)
    {
        $this->authorize('update', $post);
        $post->update($this->validated($request));

        return new PostResource($post->load('user'));
    }

    public function destroy(Post $post)
    {
        $this->authorize('delete', $post);
        $post->delete();

        return response()->noContent();
    }

    /**
     * @return array{title: string, body: string}
     */
    private function validated(Request $request): array
    {
        return $request->validate([
            'title' => ['required', 'string', 'max:120'],
            'body' => ['required', 'string'],
        ], [
            'title.required' => '제목을 입력해 주세요.',
            'body.required' => '내용을 입력해 주세요.',
        ]);
    }
}

<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Models\Comment;
use App\Models\Post;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\Gate;
use Symfony\Component\HttpFoundation\Response;

class CommentContractController extends Controller
{
    public function index(Post $post): JsonResponse
    {
        return response()->json(['data' => $post->comments()->with('user')->oldest('id')->get()->map($this->serialize(...))]);
    }

    public function store(Request $request, Post $post): JsonResponse
    {
        $data = $request->validate(['body' => ['required', 'string', 'max:1000']]);
        $comment = $post->comments()->make($data);
        $comment->user()->associate($request->user());
        $comment->save();

        return response()->json(['data' => $this->serialize($comment->load('user'))], 201);
    }

    public function destroy(Comment $comment): Response
    {
        Gate::authorize('delete', $comment);
        $comment->delete();

        return response()->noContent();
    }

    private function serialize(Comment $comment): array
    {
        return ['id' => $comment->id, 'postId' => $comment->post_id, 'body' => $comment->body,
            'author' => $comment->user ? ['id' => $comment->user->id, 'nickname' => $comment->user->name] : null,
            'createdAt' => $comment->created_at?->utc()->toISOString()];
    }
}

<?php

namespace App\Http\Controllers;

use App\Models\Comment;
use App\Models\Post;
use Illuminate\Http\Request;

class CommentController extends Controller
{
    public function store(Request $request, Post $post)
    {
        $data = $request->validate([
            'body' => ['required', 'string', 'max:1000'],
        ], [
            'body.required' => '댓글을 입력해 주세요.',
        ]);

        $post->comments()->create($data);

        return redirect()
            ->route('posts.show', $post)
            ->with('status', '댓글을 저장했습니다.');
    }

    public function destroy(Post $post, Comment $comment)
    {
        $comment->delete();

        return redirect()
            ->route('posts.show', $post)
            ->with('status', '댓글을 삭제했습니다.');
    }
}

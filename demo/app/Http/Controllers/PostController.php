<?php

namespace App\Http\Controllers;

use App\Models\Post;
use Illuminate\Http\Request;

class PostController extends Controller
{
    public function index()
    {
        return view('posts.index', [
            'posts' => Post::query()->withCount('comments')->latest()->get(),
        ]);
    }

    public function create()
    {
        return view('posts.create');
    }

    public function store(Request $request)
    {
        $data = $request->validate([
            'title' => ['required', 'string', 'max:120'],
            'body' => ['required', 'string'],
        ], [
            'title.required' => '제목을 입력해 주세요.',
            'body.required' => '내용을 입력해 주세요.',
        ]);

        $post = Post::create($data);

        return redirect()
            ->route('posts.show', $post)
            ->with('status', '글을 저장했습니다.');
    }

    public function show(Post $post)
    {
        $post->load(['comments' => fn ($query) => $query->oldest()]);

        return view('posts.show', ['post' => $post]);
    }

    public function edit(Post $post)
    {
        return view('posts.edit', ['post' => $post]);
    }

    public function update(Request $request, Post $post)
    {
        $data = $request->validate([
            'title' => ['required', 'string', 'max:120'],
            'body' => ['required', 'string'],
        ], [
            'title.required' => '제목을 입력해 주세요.',
            'body.required' => '내용을 입력해 주세요.',
        ]);

        $post->update($data);

        return redirect()
            ->route('posts.show', $post)
            ->with('status', '글을 수정했습니다.');
    }

    public function destroy(Post $post)
    {
        $post->delete();

        return redirect()
            ->route('posts.index')
            ->with('status', '글을 삭제했습니다.');
    }
}

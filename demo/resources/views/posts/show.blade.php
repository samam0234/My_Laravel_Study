@extends('layouts.app')

@section('title', $post->title)

@section('content')
    <article class="panel">
        <p class="meta">{{ $post->created_at->timezone('Asia/Seoul')->format('Y-m-d H:i') }}</p>
        <h1>{{ $post->title }}</h1>
        <p>{{ $post->body }}</p>
        <h2>댓글</h2>
        @forelse ($post->comments as $comment)
            <div class="comment">
                <p>{{ $comment->body }}</p>
                <form method="POST" action="{{ route('posts.comments.destroy', [$post, $comment]) }}">
                    @csrf
                    @method('DELETE')
                    <button class="quiet" type="submit">댓글 삭제</button>
                </form>
            </div>
        @empty
            <p class="muted">댓글이 없습니다.</p>
        @endforelse
        <form method="POST" action="{{ route('posts.comments.store', $post) }}">
            @csrf
            <label>댓글
                <textarea name="body" maxlength="1000" required>{{ old('body') }}</textarea>
            </label>
            <button type="submit">댓글 등록</button>
        </form>
        <div class="row">
            <a class="button" href="{{ route('posts.edit', $post) }}">수정</a>
            <form method="POST" action="{{ route('posts.destroy', $post) }}">
                @csrf
                @method('DELETE')
                <button class="quiet" type="submit">삭제</button>
            </form>
        </div>
    </article>
@endsection

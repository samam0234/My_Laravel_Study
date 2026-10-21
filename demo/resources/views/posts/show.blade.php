@extends('layouts.app')

@section('title', $post->title)

@section('content')
    <article class="panel">
        <p class="meta">{{ $post->created_at->timezone('Asia/Seoul')->format('Y-m-d H:i') }}</p>
        <h1>{{ $post->title }}</h1>
        <p>{{ $post->body }}</p>
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

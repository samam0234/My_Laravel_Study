@extends('layouts.app')

@section('title', '게시판')

@section('content')
    <section class="panel">
        <p class="eyebrow">study3 · CRUD</p>
        <div class="row">
            <h1>게시판</h1>
            <a class="button" href="{{ route('posts.create') }}">글쓰기</a>
        </div>
        <div class="list">
            @forelse ($posts as $post)
                <article class="card">
                    <a class="title" href="{{ route('posts.show', $post) }}">{{ $post->title }}</a>
                    <p class="meta">{{ $post->user->name ?? '작성자 없음' }} · {{ $post->created_at->timezone('Asia/Seoul')->format('Y-m-d H:i') }} · 댓글 {{ $post->comments_count }}</p>
                </article>
            @empty
                <p>아직 글이 없습니다.</p>
            @endforelse
        </div>
    </section>
@endsection

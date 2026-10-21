@extends('layouts.app')

@section('title', '게시판')

@section('content')
    <section class="panel">
        <p class="eyebrow">study3 · CRUD</p>
        <div class="row">
            <h1>게시판</h1>
            <a class="button" href="{{ route('posts.create') }}">글쓰기</a>
        </div>
        <form class="row" method="GET" action="{{ route('posts.index') }}">
            <input name="q" value="{{ request('q') }}" placeholder="제목 또는 본문">
            <button type="submit">찾기</button>
        </form>
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
        <div class="pager">
            @if ($posts->onFirstPage())
                <span class="muted">이전</span>
            @else
                <a href="{{ $posts->previousPageUrl() }}">이전</a>
            @endif
            <span>{{ $posts->currentPage() }} / {{ $posts->lastPage() }}</span>
            @if ($posts->hasMorePages())
                <a href="{{ $posts->nextPageUrl() }}">다음</a>
            @else
                <span class="muted">다음</span>
            @endif
        </div>
    </section>
@endsection

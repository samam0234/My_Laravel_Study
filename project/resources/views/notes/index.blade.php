@extends('layouts.app')

@section('title', '노트')

@section('content')
    <section class="panel">
        <div class="row">
            <h1>노트</h1>
            <a class="button" href="{{ route('notes.create') }}">새 노트</a>
        </div>
        <form class="row" method="GET" action="{{ route('notes.index') }}">
            <input name="q" value="{{ request('q') }}" placeholder="제목 또는 본문">
            <input name="tag" value="{{ request('tag') }}" placeholder="태그 이름">
            <button type="submit">찾기</button>
        </form>
        <p class="tags">
            @foreach ($tags as $tag)
                <a href="{{ route('notes.index', ['tag' => $tag->name, 'q' => request('q')]) }}">{{ $tag->name }}</a>
            @endforeach
        </p>
        <div class="list">
            @forelse ($notes as $note)
                <article class="card">
                    <a class="title" href="{{ route('notes.show', $note) }}">{{ $note->title }}</a>
                    <p class="meta">{{ $note->user->name ?? '작성자 없음' }} · {{ $note->created_at->timezone('Asia/Seoul')->format('Y-m-d H:i') }}</p>
                    <p class="tags">
                        @foreach ($note->tags as $tag)
                            <span>{{ $tag->name }}</span>
                        @endforeach
                    </p>
                </article>
            @empty
                <p>아직 노트가 없습니다.</p>
            @endforelse
        </div>
        <div class="pager">
            @if ($notes->onFirstPage())
                <span class="muted">이전</span>
            @else
                <a href="{{ $notes->previousPageUrl() }}">이전</a>
            @endif
            <span>{{ $notes->currentPage() }} / {{ $notes->lastPage() }}</span>
            @if ($notes->hasMorePages())
                <a href="{{ $notes->nextPageUrl() }}">다음</a>
            @else
                <span class="muted">다음</span>
            @endif
        </div>
    </section>
@endsection

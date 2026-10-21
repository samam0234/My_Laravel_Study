@extends('layouts.app')

@section('title', $note->title)

@section('content')
    <article class="panel">
        <p class="eyebrow">{{ $note->user->name ?? '작성자 없음' }}</p>
        <h1>{{ $note->title }}</h1>
        <p class="tags">
            @foreach ($note->tags as $tag)
                <a href="{{ route('notes.index', ['tag' => $tag->name]) }}">{{ $tag->name }}</a>
            @endforeach
        </p>
        <p class="body">{{ $note->body }}</p>
        @can('update', $note)
            <div class="row">
                <a class="button" href="{{ route('notes.edit', $note) }}">수정</a>
                <form method="POST" action="{{ route('notes.destroy', $note) }}">
                    @csrf
                    @method('DELETE')
                    <button class="quiet" type="submit">삭제</button>
                </form>
            </div>
        @endcan
    </article>
@endsection

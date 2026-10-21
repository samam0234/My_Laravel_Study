@extends('layouts.app')

@section('title', '글 수정')

@section('content')
    <section class="panel">
        <h1>글 수정</h1>
        <form method="POST" action="{{ route('posts.update', $post) }}">
            @method('PUT')
            @include('posts._form', ['post' => $post])
            <button type="submit">수정 반영</button>
        </form>
    </section>
@endsection

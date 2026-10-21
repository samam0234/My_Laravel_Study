@extends('layouts.app')

@section('title', '글쓰기')

@section('content')
    <section class="panel">
        <h1>글쓰기</h1>
        <form method="POST" action="{{ route('posts.store') }}">
            @include('posts._form')
            <button type="submit">저장</button>
        </form>
    </section>
@endsection

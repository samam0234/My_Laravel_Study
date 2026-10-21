@extends('layouts.app')

@section('title', '새 노트')

@section('content')
    <section class="panel">
        <h1>새 노트</h1>
        <form method="POST" action="{{ route('notes.store') }}">
            @include('notes._form')
            <button type="submit">저장</button>
        </form>
    </section>
@endsection

@extends('layouts.app')

@section('title', '노트 수정')

@section('content')
    <section class="panel">
        <h1>노트 수정</h1>
        <form method="POST" action="{{ route('notes.update', $note) }}">
            @method('PUT')
            @include('notes._form')
            <button type="submit">수정</button>
        </form>
    </section>
@endsection

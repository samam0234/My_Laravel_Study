@extends('layouts.app')
@section('content')
    <h1>화면 설정</h1>
    <form method="POST" action="{{ route('study.preferences.save') }}">
        @csrf
        <label for="theme">테마</label>
        <select id="theme" name="theme">
            <option value="light" @selected($theme === 'light')>밝게</option>
            <option value="dark" @selected($theme === 'dark')>어둡게</option>
        </select>
        @error('theme')<p role="alert">{{ $message }}</p>@enderror
        <button type="submit">저장</button>
    </form>
    <x-status :message="session('status')" />
@endsection

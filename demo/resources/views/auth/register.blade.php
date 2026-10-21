@extends('layouts.app')

@section('title', '회원가입')

@section('content')
    <section class="panel">
        <h1>회원가입</h1>
        <form method="POST" action="{{ route('register') }}">
            @csrf
            @if ($errors->any())
                <ul class="errors">
                    @foreach ($errors->all() as $error)
                        <li>{{ $error }}</li>
                    @endforeach
                </ul>
            @endif
            <label>이름
                <input name="name" value="{{ old('name') }}" maxlength="50" required>
            </label>
            <label>이메일
                <input name="email" type="email" value="{{ old('email') }}" autocomplete="username" required>
            </label>
            <label>비밀번호
                <input name="password" type="password" autocomplete="new-password" required>
            </label>
            <label>비밀번호 확인
                <input name="password_confirmation" type="password" autocomplete="new-password" required>
            </label>
            <button type="submit">가입</button>
        </form>
    </section>
@endsection

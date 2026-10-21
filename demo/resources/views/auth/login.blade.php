@extends('layouts.app')

@section('title', '로그인')

@section('content')
    <section class="panel">
        <p class="eyebrow">study5 · 세션</p>
        <h1>로그인</h1>
        <p class="muted">로컬 학습 계정은 mina@example.com / password123 입니다. 시드를 넣은 뒤에 들어갑니다.</p>
        <form method="POST" action="{{ route('login') }}">
            @csrf
            @if ($errors->any())
                <ul class="errors">
                    @foreach ($errors->all() as $error)
                        <li>{{ $error }}</li>
                    @endforeach
                </ul>
            @endif
            <label>이메일
                <input name="email" type="email" value="{{ old('email') }}" autocomplete="username" required>
            </label>
            <label>비밀번호
                <input name="password" type="password" autocomplete="current-password" required>
            </label>
            <label class="row">
                <input name="remember" type="checkbox" value="1" style="width:auto"> 이 브라우저에 기억
            </label>
            <button type="submit">로그인</button>
        </form>
    </section>
@endsection

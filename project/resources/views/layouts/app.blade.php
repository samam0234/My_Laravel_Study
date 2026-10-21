<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>@yield('title', '서재') · {{ config('app.name') }}</title>
    <link rel="stylesheet" href="{{ asset('css/app.css') }}">
</head>
<body>
    <header class="top">
        <a class="brand" href="{{ route('home') }}">학습 서재</a>
        <nav class="links">
            <a href="{{ route('notes.index') }}">노트</a>
            @auth
                <span>{{ auth()->user()->name }}</span>
                <form method="POST" action="{{ route('logout') }}">
                    @csrf
                    <button class="quiet" type="submit">로그아웃</button>
                </form>
            @else
                <a href="{{ route('login') }}">로그인</a>
                <a href="{{ route('register') }}">회원가입</a>
            @endauth
        </nav>
    </header>
    <main>
        @if (session('status'))
            <p class="status">{{ session('status') }}</p>
        @endif
        @yield('content')
    </main>
</body>
</html>

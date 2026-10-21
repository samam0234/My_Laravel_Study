<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>@yield('title', '첫 화면') · {{ config('app.name') }}</title>
    <link rel="stylesheet" href="{{ asset('css/app.css') }}">
</head>
<body>
    <header class="top">
        <a class="brand" href="{{ route('home') }}">{{ config('app.name') }}</a>
        <nav class="links">
            @yield('nav')
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

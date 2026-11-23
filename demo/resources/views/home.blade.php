@extends('layouts.app')

@section('title', '첫 화면')

@section('content')
    <section class="hero">
        <p class="eyebrow">study1 · Blade</p>
        <p>{{ $greeting }}</p>
        <ul>@foreach ($topics as $topic)<li>{{ $loop->iteration }}. {{ $topic }}</li>@endforeach</ul>
        <p><a href="{{ route('workspace') }}">Vue 게시판 열기</a></p>
        <h1>Laravel 게시판을 이 폴더에서 만듭니다.</h1>
        <p>라우트 <code>home</code>이 <code>HomeController</code>의 <code>index</code>를 고르고, 액션은 이 Blade를 반환합니다. 시간대는 <code>Asia/Seoul</code>, 로캘은 <code>ko</code>입니다.</p>
        <p>프레임워크 헬스 체크는 <a href="{{ url('/up') }}">/up</a> 입니다.</p>
    </section>
@endsection

@extends('layouts.app')

@section('title', '서재')

@section('content')
    <section class="hero">
        <p class="eyebrow">studyFinal · 학습 서재</p>
        <h1>읽은 것을 노트와 태그로 남깁니다.</h1>
        <p>이 사이트는 <code>demo</code> 게시판과 모델이 다릅니다. 글과 댓글 대신 노트와 태그의 다대다를 씁니다. 화면은 세션이고, <code>/api/v1</code>은 Sanctum 토큰입니다.</p>
        <p><a class="button" href="{{ route('notes.index') }}">노트 보기</a></p>
        <p class="muted">헬스 체크는 <a href="{{ url('/up') }}">/up</a> 입니다. 이 앱은 8001 포트입니다.</p>
    </section>
@endsection

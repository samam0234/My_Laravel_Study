# study5 · 폼·입력·검증

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

입력·검증·오류 표시·중복 제출 방지를 웹과 JSON 폼에 적용한다.

## ② 📖 이론

클라이언트 검증은 빠른 피드백, 서버 검증은 저장을 허용하는 최종 문이다. 브라우저 required만 믿으면 직접 HTTP 요청으로 우회할 수 있다. Blade 폼은 `@csrf`, `old()`, `@error`로 토큰·입력 복원·필드 오류를 연결한다. Vue에서는 vee-validate의 `useForm`, `defineField`, `handleSubmit`이 입력과 오류를 관리한다.

등록은 201, 조회·수정은 200, 삭제는 204다. 이 저장소의 기준 `/api`는 공통 스펙에 따라 검증 실패 400과 `error.fields`를 보낸다. Laravel 기본 JSON 검증과 이전 `/api/v1`은 422다. 같은 실패라도 422를 400으로 바꾸는 위치를 명시해 화면이 두 코드 모두 오류로 처리하게 한다. `busy`는 요청 중 버튼을 막지만 결제 같은 작업의 진짜 중복 방지는 서버의 멱등성 키가 담당한다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. Blade의 글쓰기 폼을 비워 제출하고 오류와 old 값 복원을 확인한다.
2. `/app`에서 회원가입 후 글을 등록한다. Vue submit.prevent가 전체 페이지 이동을 막고 Pinia request가 JSON을 보낸다.
3. App.vue의 run이 busy를 설정하고 finally에서 해제하는지 확인한다. 저장·삭제 실패 후에도 버튼이 다시 활성화되어야 한다.
4. 개발자도구로 200/201/204/400을 확인한다. `/api/v1`의 422도 같은 오류 처리 분기로 들어간다. 로그인은 8자부터 클라이언트 검증하고 가입은 서버가 12자 이상을 요구한다.
5. 수정은 PATCH에 바뀐 필드만 보낼 수 있다. title만 바꿔도 body·tags가 유지되는지 테스트로 확인한다.

### `demo/resources/views/posts/_form.blade.php` 전체 코드

[demo/resources/views/posts/_form.blade.php](demo/resources/views/posts/_form.blade.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```blade
@csrf
@if ($errors->any())
    <ul class="errors">
        @foreach ($errors->all() as $error)
            <li>{{ $error }}</li>
        @endforeach
    </ul>
@endif
<label>제목
    <input name="title" value="{{ old('title', $post->title ?? '') }}" maxlength="120" required>
</label>
<label>내용
    <textarea name="body" required>{{ old('body', $post->body ?? '') }}</textarea>
</label>
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 웹 POST의 위조 요청을 막는 세션 CSRF 토큰을 숨김 필드로 출력한다. |
| 2 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 3 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 4 | 서버에서 전달받은 목록을 반복해 이스케이프한 HTML을 만든다. |
| 5 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 6 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 7 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 8 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 9 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 10 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 11 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 12 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 13 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 14 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |


### `demo/app/Http/Controllers/PostController.php` 전체 코드

[demo/app/Http/Controllers/PostController.php](demo/app/Http/Controllers/PostController.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```php
<?php

namespace App\Http\Controllers;

use App\Models\Post;
use Illuminate\Http\Request;

class PostController extends Controller
{
    public function index(Request $request)
    {
        $this->authorize('viewAny', Post::class);

        $posts = Post::query()
            ->with('user')
            ->withCount('comments')
            ->search($request->query('q'))
            ->latest('id')
            ->paginate(5)
            ->withQueryString();

        return view('posts.index', ['posts' => $posts]);
    }

    public function create()
    {
        return view('posts.create');
    }

    public function store(Request $request)
    {
        $data = $request->validate([
            'title' => ['required', 'string', 'max:120'],
            'body' => ['required', 'string'],
        ], [
            'title.required' => '제목을 입력해 주세요.',
            'body.required' => '내용을 입력해 주세요.',
        ]);

        $post = $request->user()->posts()->create($data);

        return redirect()
            ->route('posts.show', $post)
            ->with('status', '글을 저장했습니다.');
    }

    public function show(Post $post)
    {
        $this->authorize('view', $post);
        $post->load(['user', 'comments' => fn ($query) => $query->with('user')->oldest()]);

        return view('posts.show', ['post' => $post]);
    }

    public function edit(Post $post)
    {
        $this->authorize('update', $post);

        return view('posts.edit', ['post' => $post]);
    }

    public function update(Request $request, Post $post)
    {
        $this->authorize('update', $post);

        $data = $request->validate([
            'title' => ['required', 'string', 'max:120'],
            'body' => ['required', 'string'],
        ], [
            'title.required' => '제목을 입력해 주세요.',
            'body.required' => '내용을 입력해 주세요.',
        ]);

        $post->update($data);

        return redirect()
            ->route('posts.show', $post)
            ->with('status', '글을 수정했습니다.');
    }

    public function destroy(Post $post)
    {
        $this->authorize('delete', $post);
        $post->delete();

        return redirect()
            ->route('posts.index')
            ->with('status', '글을 삭제했습니다.');
    }
}
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | PHP 코드 시작을 선언한다. |
| 2 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 3 | 이 클래스가 속한 이름 공간을 지정해 같은 이름의 충돌을 막는다. |
| 4 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 5 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 6 | 다른 클래스·트레이트·파사드를 현재 파일의 짧은 이름으로 가져온다. |
| 7 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 8 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 9 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 10 | `index` 메서드를 선언한다. 목록을 조회해 응답으로 반환하는 진입점이다. |
| 11 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 12 | 컨트롤러의 권한 트레이트로 정책을 실행하고 거부되면 403을 만든다. |
| 13 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 14 | 모델에 대응하는 테이블 또는 컬렉션의 조회를 시작한다. |
| 15 | 관계를 미리 조회하거나 리다이렉트의 일회성 상태값을 전달한다. |
| 16 | 관계 행 수를 추가 쿼리 반복 없이 count 필드로 읽는다. |
| 17 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 18 | 지정한 열의 내림차순으로 최근 항목을 먼저 가져온다. |
| 19 | 전체 건수와 현재 페이지를 계산하고 페이지 크기를 제한한다. |
| 20 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 21 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 22 | 명명한 Blade 뷰에 배열 값을 전달해 HTML을 렌더링한다. |
| 23 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 24 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 25 | `create` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 26 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 27 | 명명한 Blade 뷰에 배열 값을 전달해 HTML을 렌더링한다. |
| 28 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 29 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 30 | `store` 메서드를 선언한다. 검증한 입력으로 자원을 생성하는 진입점이다. |
| 31 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 32 | 서버 경계에서 입력을 검증하고 허용한 필드만 돌려받는다. |
| 33 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 34 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 35 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 36 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 37 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 38 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 39 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 40 | 검증한 속성으로 새 행을 저장하거나 작업 객체를 생성한다. |
| 41 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 42 | 처리 후 브라우저를 조회 화면으로 이동시킨다. |
| 43 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 44 | 관계를 미리 조회하거나 리다이렉트의 일회성 상태값을 전달한다. |
| 45 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 46 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 47 | `show` 메서드를 선언한다. 지정한 자원 한 건을 조회하는 진입점이다. |
| 48 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 49 | 컨트롤러의 권한 트레이트로 정책을 실행하고 거부되면 403을 만든다. |
| 50 | 관계를 미리 조회하거나 리다이렉트의 일회성 상태값을 전달한다. |
| 51 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 52 | 명명한 Blade 뷰에 배열 값을 전달해 HTML을 렌더링한다. |
| 53 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 54 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 55 | `edit` 메서드를 선언한다. 호출자에게 제공할 입력·출력 경계를 정한다. |
| 56 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 57 | 컨트롤러의 권한 트레이트로 정책을 실행하고 거부되면 403을 만든다. |
| 58 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 59 | 명명한 Blade 뷰에 배열 값을 전달해 HTML을 렌더링한다. |
| 60 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 61 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 62 | `update` 메서드를 선언한다. 소유권 확인 뒤 전달된 필드만 수정하는 진입점이다. |
| 63 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 64 | 컨트롤러의 권한 트레이트로 정책을 실행하고 거부되면 403을 만든다. |
| 65 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 66 | 서버 경계에서 입력을 검증하고 허용한 필드만 돌려받는다. |
| 67 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 68 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 69 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 70 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 71 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 72 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 73 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 74 | 이미 확인한 행에 전달된 변경값을 저장한다. |
| 75 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 76 | 처리 후 브라우저를 조회 화면으로 이동시킨다. |
| 77 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 78 | 관계를 미리 조회하거나 리다이렉트의 일회성 상태값을 전달한다. |
| 79 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 80 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 81 | `destroy` 메서드를 선언한다. 권한 확인 뒤 자원을 삭제하는 진입점이다. |
| 82 | 현재 선언·조건·설정의 내부 블록을 연다. |
| 83 | 컨트롤러의 권한 트레이트로 정책을 실행하고 거부되면 403을 만든다. |
| 84 | 대상 행·토큰·파일을 제거한다. 앞선 소유권 검사를 함께 읽는다. |
| 85 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 86 | 처리 후 브라우저를 조회 화면으로 이동시킨다. |
| 87 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 88 | 관계를 미리 조회하거나 리다이렉트의 일회성 상태값을 전달한다. |
| 89 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 90 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `demo/resources/js/App.vue` 전체 코드

[demo/resources/js/App.vue](demo/resources/js/App.vue)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```vue
<script setup>
import { onMounted, ref } from 'vue';
import { useForm } from 'vee-validate';
import { useAuth } from './stores/auth';
const props = defineProps({ advanced: Boolean });
const auth = useAuth();
const entries = ref([]), meta = ref({ page: 1, totalPages: 1 }), query = ref('');
const message = ref(''), busy = ref(false), signup = ref(false), editing = ref(null);
const title = ref(''), body = ref(''), tags = ref('');
const documents = ref([]), file = ref(null), selectedDocument = ref(null), question = ref(''), answer = ref('');
const notifications = ref([]), comments = ref({}), replies = ref({});
async function showComments(id) { comments.value[id] = (await auth.request(`/api/posts/${id}/comments`)).data; }
async function reply(id) { await run(async () => { await auth.request(`/api/posts/${id}/comments`, { method: 'POST', body: JSON.stringify({ body: replies.value[id] }) }); replies.value[id] = ''; await showComments(id); }); }
async function removeComment(id, postId) { await run(async () => { await auth.request(`/api/comments/${id}`, { method: 'DELETE' }); await showComments(postId); }); }
const { defineField, handleSubmit, errors, setErrors } = useForm({
    initialValues: { email: '', password: '', nickname: '' },
    validationSchema: {
        email: value => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value || '') || '이메일을 입력하세요.',
        password: value => (value?.length >= 8) || '비밀번호는 8자 이상입니다.',
    },
});
const [email, emailAttrs] = defineField('email');
const [password, passwordAttrs] = defineField('password');
const [nickname, nicknameAttrs] = defineField('nickname');
async function run(action) {
    if (busy.value) return;
    busy.value = true; message.value = '';
    try { await action(); }
    catch (error) { message.value = `${error.status || ''} ${error.message}`; setErrors(error.fields || {}); }
    finally { busy.value = false; }
}
async function load(page = 1) {
    const result = await auth.request(`/api/posts?${new URLSearchParams({ q: query.value, page, limit: 5 })}`);
    entries.value = result.data; meta.value = result.meta;
}
async function loadDocuments() {
    if (!props.advanced || !auth.user) return;
    documents.value = (await auth.request('/api/documents')).data;
    notifications.value = (await auth.request('/api/notifications')).data;
}
const submitLogin = handleSubmit(values => run(async () => {
    await auth.login(values, signup.value);
    await load(); await loadDocuments();
}));
function edit(entry) { editing.value = entry.id; title.value = entry.title; body.value = entry.body; tags.value = entry.tags.join(', '); }
function reset() { editing.value = null; title.value = ''; body.value = ''; tags.value = ''; }
async function save() {
    await run(async () => {
        await auth.request(`/api/posts${editing.value ? `/${editing.value}` : ''}`, {
            method: editing.value ? 'PATCH' : 'POST',
            body: JSON.stringify({ title: title.value, body: body.value, tags: tags.value.split(',').map(x => x.trim()).filter(Boolean) }),
        });
        reset(); await load(); message.value = '저장했습니다.';
    });
}
async function remove(entry) {
    if (!window.confirm(`“${entry.title}”을 삭제할까요?`)) return;
    await run(async () => { await auth.request(`/api/posts/${entry.id}`, { method: 'DELETE' }); await load(); });
}
async function logout() { await run(async () => { await auth.logout(); documents.value = []; notifications.value = []; reset(); }); }
async function upload() {
    await run(async () => {
        const form = new FormData(); form.append('file', file.value);
        await auth.request('/api/documents', { method: 'POST', body: form });
        await loadDocuments(); message.value = '업로드했습니다. 큐 워커 처리 후 새로고침하세요.';
    });
}
async function ask() {
    await run(async () => {
        answer.value = '';
        const response = await fetch(`/api/documents/${selectedDocument.value}/ask`, {
            method: 'POST', headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream', Authorization: `Bearer ${auth.token}` },
            body: JSON.stringify({ question: question.value }),
        });
        if (!response.ok) throw new Error((await response.json()).error?.message || 'AI 요청 실패');
        const reader = response.body.getReader(), decoder = new TextDecoder(); let buffer = '';
        while (true) {
            const { done, value } = await reader.read();
            buffer += decoder.decode(value, { stream: !done });
            let end;
            while ((end = buffer.indexOf('\n\n')) >= 0) {
                const event = buffer.slice(0, end); buffer = buffer.slice(end + 2);
                const data = event.split('\n').find(line => line.startsWith('data: '));
                if (!data) continue;
                const payload = JSON.parse(data.slice(6));
                if (payload.error) throw new Error(payload.error);
                answer.value += payload.delta || '';
            }
            if (done) break;
        }
    });
}
onMounted(() => run(() => load()));
</script>

<template>
    <main class="container py-4" style="max-width: 960px">
        <header class="d-flex justify-content-between align-items-center mb-4">
            <h1 class="h3">{{ advanced ? '학습 서재 · 문서 도우미' : 'Laravel 게시판' }}</h1>
            <a href="/">Blade 홈</a>
        </header>
        <p v-if="message" role="status" class="alert alert-info">{{ message }}</p>
        <section v-if="!auth.user" class="card card-body mb-4">
            <h2 class="h5">{{ signup ? '회원가입' : '로그인' }}</h2>
            <form @submit.prevent="submitLogin" class="d-grid gap-2">
                <label v-if="signup">닉네임 <input v-model="nickname" v-bind="nicknameAttrs" class="form-control" required maxlength="80"></label>
                <label>이메일 <input v-model="email" v-bind="emailAttrs" type="email" class="form-control" autocomplete="username"></label>
                <p v-if="errors.email" class="text-danger">{{ errors.email }}</p>
                <label>비밀번호 <input v-model="password" v-bind="passwordAttrs" type="password" :autocomplete="signup ? 'new-password' : 'current-password'" class="form-control"></label>
                <p v-if="errors.password" class="text-danger">{{ errors.password }}</p>
                <small v-if="signup">회원가입 비밀번호는 서버에서 12자 이상을 검사합니다.</small>
                <button :disabled="busy" class="btn btn-primary">{{ signup ? '가입' : '로그인' }}</button>
            </form>
            <button @click="signup = !signup" class="btn btn-link">{{ signup ? '로그인으로' : '회원가입으로' }}</button>
            <a v-if="advanced" href="/auth/github">GitHub 로그인 (Blade 세션)</a>
        </section>
        <div v-else class="d-flex gap-3 mb-3"><span>{{ auth.user.nickname }}</span><button @click="logout" :disabled="busy" class="btn btn-outline-secondary btn-sm">로그아웃</button></div>
        <form class="d-flex gap-2 mb-3" @submit.prevent="run(() => load())">
            <label class="visually-hidden" for="search">제목·본문 검색</label>
            <input id="search" v-model="query" class="form-control" placeholder="제목·본문 검색">
            <button :disabled="busy" class="btn btn-secondary">검색</button>
        </form>
        <article v-for="entry in entries" :key="entry.id" class="card card-body mb-2">
            <h2 class="h5">{{ entry.title }}</h2><p style="white-space: pre-wrap">{{ entry.body }}</p>
            <small>{{ entry.author?.nickname || '탈퇴 회원' }} · {{ entry.tags.join(', ') }} · {{ new Date(entry.createdAt).toLocaleString() }}</small>
            <div v-if="auth.user?.id === entry.author?.id" class="mt-2 d-flex gap-2">
                <button @click="edit(entry)" class="btn btn-sm btn-outline-primary">수정</button>
                <button @click="remove(entry)" :disabled="busy" class="btn btn-sm btn-outline-danger">삭제</button>
            </div>
            <button @click="run(() => showComments(entry.id))" :disabled="busy" class="btn btn-link text-start">댓글 보기</button>
            <ul v-if="comments[entry.id]"><li v-for="comment in comments[entry.id]" :key="comment.id">{{ comment.body }} · {{ comment.author?.nickname }} <button v-if="auth.user?.id === comment.author?.id" @click="removeComment(comment.id, entry.id)" :disabled="busy" class="btn btn-link btn-sm">댓글 삭제</button></li></ul>
            <form v-if="auth.user" @submit.prevent="reply(entry.id)" class="d-flex gap-2"><label class="flex-grow-1">댓글 <input v-model="replies[entry.id]" required maxlength="1000" class="form-control"></label><button :disabled="busy" class="btn btn-outline-primary">등록</button></form>
        </article>
        <nav class="d-flex gap-3 my-3" aria-label="목록 페이지">
            <button @click="run(() => load(meta.page - 1))" :disabled="busy || meta.page <= 1" class="btn btn-outline-secondary">이전</button>
            <span>{{ meta.page }} / {{ meta.totalPages }}</span>
            <button @click="run(() => load(meta.page + 1))" :disabled="busy || meta.page >= meta.totalPages" class="btn btn-outline-secondary">다음</button>
        </nav>
        <form v-if="auth.user" @submit.prevent="save" class="card card-body d-grid gap-2">
            <h2 class="h5">{{ editing ? '수정' : '새 글' }}</h2>
            <label>제목 <input v-model="title" required maxlength="200" class="form-control"></label>
            <p v-if="errors.title" class="text-danger">{{ errors.title }}</p>
            <label>본문 <textarea v-model="body" required maxlength="20000" class="form-control" rows="4"></textarea></label>
            <p v-if="errors.body" class="text-danger">{{ errors.body }}</p>
            <label>태그 (쉼표로 구분) <input v-model="tags" class="form-control"></label>
            <button :disabled="busy" class="btn btn-primary">저장</button>
            <button v-if="editing" type="button" @click="reset" class="btn btn-light">수정 취소</button>
        </form>
        <section v-if="advanced && auth.user" class="card card-body mt-4 d-grid gap-3">
            <h2 class="h5">DocuForge 학습 기능: 텍스트 문서 요약·근거 질문</h2>
            <p>기본 설정은 mock입니다. 실제 AI는 AI_DRIVER=ollama로 전환합니다. TXT/MD, UTF-8, 최대 100KB.</p>
            <form @submit.prevent="upload" class="d-grid gap-2">
                <label>문서 파일 <input type="file" accept=".txt,.md" required @change="file = $event.target.files[0]" class="form-control"></label>
                <button :disabled="busy" class="btn btn-primary">업로드·요약 예약</button>
            </form>
            <button @click="run(loadDocuments)" :disabled="busy" class="btn btn-outline-secondary">문서·알림 새로고침</button>
            <ul><li v-for="document in documents" :key="document.id">{{ document.filename }} · {{ document.status }}<p>{{ document.summary }}</p></li></ul>
            <form @submit.prevent="ask" class="d-grid gap-2">
                <label>문서 선택 <select v-model="selectedDocument" required class="form-select"><option v-for="document in documents" :key="document.id" :value="document.id">{{ document.filename }}</option></select></label>
                <label>질문 <input v-model="question" required maxlength="1000" class="form-control"></label>
                <button :disabled="busy" class="btn btn-primary">스트리밍 질문</button>
            </form>
            <pre aria-live="polite" style="white-space: pre-wrap">{{ answer }}</pre>
            <h3 class="h6">알림</h3><ul><li v-for="notification in notifications" :key="notification.id">{{ notification.data.message }}</li></ul>
        </section>
    </main>
</template>
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 2 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 3 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 4 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 5 | 부모 또는 마운트 진입점에서 전달받는 읽기 전용 입력을 선언한다. |
| 6 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 7 | 화면이 변경을 관찰할 반응형 상태를 초기화한다. |
| 8 | 화면이 변경을 관찰할 반응형 상태를 초기화한다. |
| 9 | 화면이 변경을 관찰할 반응형 상태를 초기화한다. |
| 10 | 화면이 변경을 관찰할 반응형 상태를 초기화한다. |
| 11 | 화면이 변경을 관찰할 반응형 상태를 초기화한다. |
| 12 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 13 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 14 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 15 | 폼 입력·오류 상태를 필드와 연결한다. |
| 16 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 17 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 18 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 19 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 20 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 21 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 22 | 폼 입력·오류 상태를 필드와 연결한다. |
| 23 | 폼 입력·오류 상태를 필드와 연결한다. |
| 24 | 폼 입력·오류 상태를 필드와 연결한다. |
| 25 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 26 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 27 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 28 | 실패 처리와 정리 동작을 분리해 부분 결과를 성공으로 취급하지 않는다. |
| 29 | 실패 처리와 정리 동작을 분리해 부분 결과를 성공으로 취급하지 않는다. |
| 30 | 실패 처리와 정리 동작을 분리해 부분 결과를 성공으로 취급하지 않는다. |
| 31 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 32 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 33 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 34 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 35 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 36 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 37 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 38 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 39 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 40 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 41 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 42 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 43 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 44 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 45 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 46 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 47 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 48 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 49 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 50 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 51 | 브라우저 상태를 API 요청 JSON 본문으로 변환한다. |
| 52 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 53 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 54 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 55 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 56 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 57 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 58 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 59 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 60 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 61 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 62 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 63 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 64 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 65 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 66 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 67 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 68 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 69 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 70 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 71 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 72 | 현재 메모리 토큰을 Bearer 인증 헤더에 연결한다. |
| 73 | 브라우저 상태를 API 요청 JSON 본문으로 변환한다. |
| 74 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 75 | 응답 JSON을 화면에서 다룰 객체로 변환한다. |
| 76 | 스트림 조각 사이에 걸친 한글 UTF-8 바이트를 보존하며 디코딩한다. |
| 77 | 목록·청크·응답 스트림의 각 항목을 순서대로 처리한다. |
| 78 | 서버 스트림의 다음 데이터 조각이 도착할 때까지 읽는다. |
| 79 | 스트림 조각 사이에 걸친 한글 UTF-8 바이트를 보존하며 디코딩한다. |
| 80 | 현재 모듈이 사용할 값 또는 외부에 제공할 인터페이스를 선언한다. |
| 81 | 목록·청크·응답 스트림의 각 항목을 순서대로 처리한다. |
| 82 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 83 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 84 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 85 | 응답 JSON을 화면에서 다룰 객체로 변환한다. |
| 86 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 87 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 88 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 89 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 90 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 91 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 92 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 93 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 94 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 95 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 96 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 97 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 98 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 99 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 100 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 101 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 102 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 103 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 104 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 105 | 폼의 기본 페이지 이동을 막고 정의한 제출 동작을 실행한다. |
| 106 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 107 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 108 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 109 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 110 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 111 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 112 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 113 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 114 | 클릭 이벤트를 화면 동작에 연결한다. |
| 115 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 116 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 117 | 클릭 이벤트를 화면 동작에 연결한다. |
| 118 | 폼의 기본 페이지 이동을 막고 정의한 제출 동작을 실행한다. |
| 119 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 120 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 121 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 122 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 123 | 목록 상태를 key로 구분해 반복 렌더링한다. |
| 124 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 125 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 126 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 127 | 클릭 이벤트를 화면 동작에 연결한다. |
| 128 | 클릭 이벤트를 화면 동작에 연결한다. |
| 129 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 130 | 클릭 이벤트를 화면 동작에 연결한다. |
| 131 | 목록 상태를 key로 구분해 반복 렌더링한다. |
| 132 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 133 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 134 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 135 | 클릭 이벤트를 화면 동작에 연결한다. |
| 136 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 137 | 클릭 이벤트를 화면 동작에 연결한다. |
| 138 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 139 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 140 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 141 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 142 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 143 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 144 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 145 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 146 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 147 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 148 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 149 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 150 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 151 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 152 | 폼의 기본 페이지 이동을 막고 정의한 제출 동작을 실행한다. |
| 153 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 154 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 155 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 156 | 클릭 이벤트를 화면 동작에 연결한다. |
| 157 | 목록 상태를 key로 구분해 반복 렌더링한다. |
| 158 | 폼의 기본 페이지 이동을 막고 정의한 제출 동작을 실행한다. |
| 159 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 160 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 161 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 162 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 163 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 164 | 목록 상태를 key로 구분해 반복 렌더링한다. |
| 165 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 166 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 167 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |


## ④ 🔗 연동 포인트

폼의 필드 이름 title/body/tags는 다음 단계 API 스키마로 이어진다. 서버 검증 후에만 모델을 만들며 user_id는 클라이언트가 결정하지 못한다. Stripe의 멱등성은 study13에서 서버로 확장한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 419 Page Expired | 웹 POST의 CSRF 토큰·세션 만료 | @csrf와 세션 쿠키 확인, 화면 재진입 |
| 오류가 필드에 안 보임 | error.fields와 라이브러리 오류 상태를 연결하지 않음 | setErrors(error.fields) 호출 확인 |
| 두 번 저장됨 | busy 설정 전에 요청을 중복 실행함 | 폼 이벤트와 버튼 클릭을 이중 연결하지 않고 서버 멱등성도 별도 설계 |

## ⑥ 직접 해보기

1. 개발자도구에서 required를 지우고 서버 검증 실패를 재현한다.
2. 제목만 PATCH하고 본문이 유지되는지 확인한다.
3. 응답을 지연시켜 저장 버튼 비활성화를 확인한다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] 입력·old·필드 오류를 연결했다.
- [ ] 200·400·422의 화면 흐름을 설명했다.
- [ ] 중복 제출 방지와 서버 멱등성을 구분했다.

## ⑧ 다음 단계 연결

입력·검증·오류 표시·중복 제출 방지를 웹과 JSON 폼에 적용한다. 이 결과를 [study6.md](study6.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://laravel.com/docs/13.x/validation)

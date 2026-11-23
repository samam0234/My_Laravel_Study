# study12 · 프론트·UI 연동

학습 기준: [Laravel 노션](https://app.notion.com/p/3fdd7dec5e2e81299ce9e33e7ba75edf) · 단일 구성: Laravel + Vue · [전체 순서](README.md)

이 저장소는 완성된 학습 소스를 제공한다. 기초는 `demo/`, 심화는 `project/`에서 실행한다. 단계별 파일은 기존 study 문서를 덮어써 갱신했으며, 아래 소스는 현재 저장소의 실제 전문이다. 처음부터 만들 때는 해당 경로의 파일과 앞 단계의 준비를 함께 적용한다.

## ① 목표 한 줄

Vue·Bootstrap·Pinia·vee-validate로 서재의 입력·인증·목록을 연결한다.

## ② 📖 이론

Vue SFC는 script setup과 template을 한 컴포넌트에 모은다. Bootstrap은 화면 프레임워크를 추가하지 않고 CSS 유틸과 접근 가능한 기본 요소를 제공한다. Pinia는 token/user와 공통 요청 행동, vee-validate는 폼 입력과 오류 상태를 맡는다. 각각 화면의 옷·공용 기억·입력 안내원으로 비유할 수 있다.

이 저장소는 Vue 한 가지를 사용한다. Laravel의 /app HTML이 Vue를 마운트하고 같은 호스트의 /api를 호출한다. Vite 개발 서버는 자산만 제공한다. 운영에서는 PHP-FPM·Nginx가 빌드 파일과 요청을 함께 제공하므로 프론트용 별도 앱 서버가 없다.

## ③ 🛠️ 실기 · 전체 코드와 줄별 설명

1. npm ci로 잠금 파일의 Vue·Pinia·vee-validate·Bootstrap을 설치한다. 기존 JS/TS 화면별 폴더를 다시 만들지 않는다.
2. app.js의 createApp과 createPinia, App.vue의 props·ref·이벤트를 연결한다.
3. login → accessToken → 공통 Authorization → 목록/저장 → 오류 fields 순서를 Network에서 추적한다. 기준 API의 data/meta와 camelCase 필드를 그대로 읽는다.
4. 제목·본문·태그·댓글을 등록하고 자기 글에만 수정·삭제 버튼이 보이는지 확인한다. 버튼 노출과 서버 Policy를 함께 적용한다.
5. 로그인/가입은 useForm으로, 글쓰기 입력은 v-model과 서버 errors로 관리한다. busy로 중복 요청을 막고 키보드 label·role=status를 유지한다.
6. 개발은 PHP 주소 /app에 접속하고 npm run dev를 병행한다. 운영은 npm run build를 사용한다. project의 실시간 알림 연결은 study17에서 확장한다.

### `project/resources/js/app.js` 전체 코드

[project/resources/js/app.js](project/resources/js/app.js)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```javascript
import { createApp } from 'vue';
import { createPinia } from 'pinia';
import 'bootstrap/dist/css/bootstrap.min.css';
import App from './App.vue';
const element = document.querySelector('#app');
createApp(App, { advanced: element.dataset.advanced === 'true' }).use(createPinia()).mount(element);
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 2 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 3 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 4 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 5 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 6 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |


### `project/resources/js/stores/auth.js` 전체 코드

[project/resources/js/stores/auth.js](project/resources/js/stores/auth.js)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```javascript
import { defineStore } from 'pinia';
import { ref } from 'vue';
export const useAuth = defineStore('auth', () => {
    const token = ref('');
    const user = ref(null);
    async function request(path, options = {}) {
        const headers = { Accept: 'application/json', ...options.headers };
        if (token.value) headers.Authorization = `Bearer ${token.value}`;
        if (options.body && !(options.body instanceof FormData)) headers['Content-Type'] = 'application/json';
        const response = await fetch(path, { ...options, headers });
        const body = response.status === 204 ? null : await response.json();
        if (!response.ok) {
            if (response.status === 401) { token.value = ''; user.value = null; }
            const error = new Error(body?.error?.message || '요청 실패');
            error.fields = body?.error?.fields || {};
            error.status = response.status;
            throw error;
        }
        return body;
    }
    async function login(values, signup = false) {
        const result = await request(`/api/auth/${signup ? 'signup' : 'login'}`, { method: 'POST', body: JSON.stringify(values) });
        token.value = result.data.accessToken;
        user.value = result.data.user;
    }
    async function logout() {
        try { await request('/api/auth/logout', { method: 'POST' }); }
        finally { token.value = ''; user.value = null; }
    }
    return { token, user, request, login, logout };
});
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 2 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 3 | 여러 화면 함수가 공유할 Pinia 상태와 행동을 정의한다. |
| 4 | 화면이 변경을 관찰할 반응형 상태를 초기화한다. |
| 5 | 화면이 변경을 관찰할 반응형 상태를 초기화한다. |
| 6 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 7 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 8 | 현재 메모리 토큰을 Bearer 인증 헤더에 연결한다. |
| 9 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 10 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 11 | 응답 JSON을 화면에서 다룰 객체로 변환한다. |
| 12 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 13 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 14 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 15 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 16 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 17 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 18 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 19 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 20 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 21 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 22 | 브라우저 상태를 API 요청 JSON 본문으로 변환한다. |
| 23 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 24 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 25 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 26 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 27 | 실패 처리와 정리 동작을 분리해 부분 결과를 성공으로 취급하지 않는다. |
| 28 | 실패 처리와 정리 동작을 분리해 부분 결과를 성공으로 취급하지 않는다. |
| 29 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 30 | 구성한 값·모델·응답을 현재 함수의 호출자에게 돌려준다. |
| 31 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |


### `project/resources/js/App.vue` 전체 코드

[project/resources/js/App.vue](project/resources/js/App.vue)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```vue
<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import { connect, disconnect } from './realtime';
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
    await load(); await loadDocuments(); connect(auth, () => run(loadDocuments));
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
async function logout() { await run(async () => { disconnect(); await auth.logout(); documents.value = []; notifications.value = []; reset(); }); }
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
onUnmounted(disconnect);
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
| 5 | 번들러가 Vue·라이브러리·공통 모듈 또는 CSS 의존성을 가져온다. |
| 6 | 부모 또는 마운트 진입점에서 전달받는 읽기 전용 입력을 선언한다. |
| 7 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 8 | 화면이 변경을 관찰할 반응형 상태를 초기화한다. |
| 9 | 화면이 변경을 관찰할 반응형 상태를 초기화한다. |
| 10 | 화면이 변경을 관찰할 반응형 상태를 초기화한다. |
| 11 | 화면이 변경을 관찰할 반응형 상태를 초기화한다. |
| 12 | 화면이 변경을 관찰할 반응형 상태를 초기화한다. |
| 13 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 14 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 15 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 16 | 폼 입력·오류 상태를 필드와 연결한다. |
| 17 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 18 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 19 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 20 | 민감한 인증 설정의 참조 또는 예시 자리다. 실제 값은 환경·비밀 저장소에만 둔다. |
| 21 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 22 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 23 | 폼 입력·오류 상태를 필드와 연결한다. |
| 24 | 폼 입력·오류 상태를 필드와 연결한다. |
| 25 | 폼 입력·오류 상태를 필드와 연결한다. |
| 26 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 27 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 28 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 29 | 실패 처리와 정리 동작을 분리해 부분 결과를 성공으로 취급하지 않는다. |
| 30 | 실패 처리와 정리 동작을 분리해 부분 결과를 성공으로 취급하지 않는다. |
| 31 | 실패 처리와 정리 동작을 분리해 부분 결과를 성공으로 취급하지 않는다. |
| 32 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 33 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 34 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 35 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 36 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 37 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 38 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 39 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 40 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 41 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 42 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 43 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 44 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 45 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 46 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 47 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 48 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 49 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 50 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 51 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 52 | 브라우저 상태를 API 요청 JSON 본문으로 변환한다. |
| 53 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 54 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 55 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 56 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 57 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 58 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 59 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 60 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 61 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 62 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 63 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 64 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 65 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 66 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 67 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 68 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 69 | 재사용할 화면 동작을 함수로 선언한다. async 함수는 HTTP 완료를 기다릴 수 있다. |
| 70 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 71 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 72 | 같은 Laravel 서버에 비동기 HTTP 요청을 보낸다. |
| 73 | 현재 메모리 토큰을 Bearer 인증 헤더에 연결한다. |
| 74 | 브라우저 상태를 API 요청 JSON 본문으로 변환한다. |
| 75 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 76 | 응답 JSON을 화면에서 다룰 객체로 변환한다. |
| 77 | 스트림 조각 사이에 걸친 한글 UTF-8 바이트를 보존하며 디코딩한다. |
| 78 | 목록·청크·응답 스트림의 각 항목을 순서대로 처리한다. |
| 79 | 서버 스트림의 다음 데이터 조각이 도착할 때까지 읽는다. |
| 80 | 스트림 조각 사이에 걸친 한글 UTF-8 바이트를 보존하며 디코딩한다. |
| 81 | 현재 모듈이 사용할 값 또는 외부에 제공할 인터페이스를 선언한다. |
| 82 | 목록·청크·응답 스트림의 각 항목을 순서대로 처리한다. |
| 83 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 84 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 85 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 86 | 응답 JSON을 화면에서 다룰 객체로 변환한다. |
| 87 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 88 | 이후 처리에 사용할 값이나 의존성을 변수·객체 속성에 저장한다. |
| 89 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 90 | 조건을 검사해 성공·실패 또는 선택 기능의 흐름을 나눈다. |
| 91 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 92 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 93 | 현재 블록·배열·호출을 닫고 상위 흐름으로 돌아간다. |
| 94 | 배열·객체·설정의 키에 값 또는 처리 함수를 연결한다. |
| 95 | 앞서 선언한 처리의 연속 구문이다. 같은 함수·설정 블록의 입력과 결과에 연결된다. |
| 96 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 97 | 가독성을 위한 빈 줄이며 실행 동작은 없다. |
| 98 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 99 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 100 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 101 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 102 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 103 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 104 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 105 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 106 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 107 | 폼의 기본 페이지 이동을 막고 정의한 제출 동작을 실행한다. |
| 108 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 109 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 110 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 111 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 112 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 113 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 114 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 115 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 116 | 클릭 이벤트를 화면 동작에 연결한다. |
| 117 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 118 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 119 | 클릭 이벤트를 화면 동작에 연결한다. |
| 120 | 폼의 기본 페이지 이동을 막고 정의한 제출 동작을 실행한다. |
| 121 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 122 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 123 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 124 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 125 | 목록 상태를 key로 구분해 반복 렌더링한다. |
| 126 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 127 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 128 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 129 | 클릭 이벤트를 화면 동작에 연결한다. |
| 130 | 클릭 이벤트를 화면 동작에 연결한다. |
| 131 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 132 | 클릭 이벤트를 화면 동작에 연결한다. |
| 133 | 목록 상태를 key로 구분해 반복 렌더링한다. |
| 134 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 135 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 136 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 137 | 클릭 이벤트를 화면 동작에 연결한다. |
| 138 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 139 | 클릭 이벤트를 화면 동작에 연결한다. |
| 140 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 141 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 142 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 143 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 144 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 145 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 146 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 147 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 148 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 149 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 150 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 151 | 인증·상태·오류 조건에 맞는 UI만 렌더링한다. |
| 152 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 153 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 154 | 폼의 기본 페이지 이동을 막고 정의한 제출 동작을 실행한다. |
| 155 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 156 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 157 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 158 | 클릭 이벤트를 화면 동작에 연결한다. |
| 159 | 목록 상태를 key로 구분해 반복 렌더링한다. |
| 160 | 폼의 기본 페이지 이동을 막고 정의한 제출 동작을 실행한다. |
| 161 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 162 | 입력 요소와 Vue 상태를 양방향으로 묶는다. DB 저장은 별도 요청이다. |
| 163 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 164 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 165 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 166 | 목록 상태를 key로 구분해 반복 렌더링한다. |
| 167 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 168 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 169 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |


### `project/resources/views/workspace.blade.php` 전체 코드

[project/resources/views/workspace.blade.php](project/resources/views/workspace.blade.php)를 해당 경로에 둔다. 아래 블록에는 생략된 코드가 없다.

```blade
<!doctype html>
<html lang="ko"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Laravel 학습 서재</title>@vite('resources/js/app.js')</head>
<body><div id="app" data-advanced="true"></div></body></html>
```

#### 줄별 설명

| 줄 | 설명 |
|---:|---|
| 1 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 2 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 3 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |
| 4 | 화면 요소·접근성 속성·텍스트 영역을 선언한다. 중괄호 출력은 기본 이스케이프한다. |


## ④ 🔗 연동 포인트

study6·14에서 맞춘 API 계약을 실제 Vue 화면이 소비한다. DB 교체와 무관하게 화면 요청 경로는 /api다. 다음 단계에서는 서버만 외부 서비스 키를 갖고 Vue에는 성공·실패 결과만 전달한다.

## ⑤ 오류 노트

| 증상 | 원인 | 해결 |
|---|---|---|
| 401 후 화면이 로그인 상태 | 인증 실패 때 store를 지우지 않음 | request 함수의 token/user 초기화 확인 |
| Vue가 마운트되지 않음 | 진입점·DOM id·Vite manifest 불일치 | #app과 @vite, 빌드 입력 확인 |
| 한글이 중간에 깨짐 | 스트림 바이트를 매번 독립 디코딩 | TextDecoder stream 옵션 사용 |

## ⑥ 직접 해보기

1. 화면에서 가입→글→수정→댓글→삭제→로그아웃을 수행한다.
2. Network를 offline으로 바꾸고 오류와 busy 해제를 확인한다.
3. 키보드만으로 폼 label과 버튼에 접근한다.

## ⑦ ☐ 체크리스트

학습자가 직접 실행·설명한 뒤 체크한다. 코드 준비 완료와 외부 서비스 실행 검증은 다르다.

- [ ] Vue / React / Svelte를 프론트로 붙이기 (선택)
- [ ] 선택 목표 "Vue / React / Svelte를 프론트로 붙이기": 위 항목을 맞춘 뒤 기존 프론트 게시판을 그대로 연결해 보기
- [ ] Vue 1개와 Laravel의 단일 배포 구성을 확인했다.
- [ ] Pinia·폼 오류·UI CSS를 연결했다.

## ⑧ 다음 단계 연결

Vue·Bootstrap·Pinia·vee-validate로 서재의 입력·인증·목록을 연결한다. 이 결과를 [study13.md](study13.md)에서 다음 실습과 연결한다.

### 근거·참고

[공통 API 스펙 v1](https://app.notion.com/p/3d6d7dec5e2e8139adbfd36dd506c65e) · [요구사항 매핑](docs/notion-coverage.md) · [검증 기록](docs/verification.md)

- [공식 문서 1](https://vuejs.org/guide/introduction.html)
- [공식 문서 2](https://v3--pinia-official.netlify.app/core-concepts/)
- [공식 문서 3](https://vee-validate.logaretm.com/v4/guide/composition-api/getting-started/)
- [공식 문서 4](https://getbootstrap.com/docs/5.3/getting-started/introduction/)

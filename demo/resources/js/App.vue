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

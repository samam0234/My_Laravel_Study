import {
  commentsUrl,
  loginUrl,
  logoutUrl,
  postUrl,
  postsUrl,
  requestJson,
  type Comment,
  type Page,
  type Post,
  type Resource,
  type TokenResponse
} from "./api";

const origin = "http://127.0.0.1:8000";
const tokenKey = "laravel.demo.ts.token";
const nameKey = "laravel.demo.ts.name";
const state = {
  token: readStore(tokenKey),
  name: readStore(nameKey),
  page: 1,
  per: 5,
  q: "",
  postId: null as number | null
};

const status = required<HTMLElement>("#status");
const posts = required<HTMLElement>("#posts");
const meta = required<HTMLElement>("#meta");
const detail = required<HTMLElement>("#detail");
const detailTitle = required<HTMLElement>("#detail-title");
const detailBody = required<HTMLElement>("#detail-body");
const detailAuthor = required<HTMLElement>("#detail-author");
const comments = required<HTMLElement>("#comments");
const prev = required<HTMLButtonElement>("#prev");
const next = required<HTMLButtonElement>("#next");

function required<T extends Element>(selector: string): T {
  const element = document.querySelector<T>(selector);
  if (!element) throw new Error(`missing ${selector}`);
  return element;
}

function readStore(key: string): string {
  try {
    return sessionStorage.getItem(key) || "";
  } catch {
    return "";
  }
}

function writeStore(key: string, value: string): void {
  try {
    if (value) sessionStorage.setItem(key, value);
    else sessionStorage.removeItem(key);
  } catch {
    // 저장소를 못 쓰면 메모리 상태만 유지한다.
  }
}

function setStatus(text: string, isError = false): void {
  status.textContent = text;
  status.classList.toggle("error", isError);
}

function showSession(): void {
  setStatus(state.token ? `${state.name} 로그인` : "로그인 전입니다. 목록은 볼 수 있습니다.");
}

async function loadPosts(): Promise<void> {
  const data = await requestJson<Page<Post>>(postsUrl(origin, state));
  posts.replaceChildren();
  for (const post of data.data) {
    const article = document.createElement("article");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "link";
    button.textContent = post.title;
    button.addEventListener("click", () => {
      void openPost(post.id);
    });
    const line = document.createElement("p");
    line.className = "muted";
    line.textContent = post.author ?? "작성자 없음";
    article.append(button, line);
    posts.append(article);
  }
  meta.textContent = `${data.meta.total}건 · ${data.meta.current_page} / ${data.meta.last_page}`;
  prev.disabled = data.meta.current_page <= 1;
  next.disabled = data.meta.current_page >= data.meta.last_page;
}

async function openPost(id: number): Promise<void> {
  const post = await requestJson<Resource<Post>>(postUrl(origin, id));
  const commentPage = await requestJson<Resource<Comment[]>>(commentsUrl(origin, id));
  state.postId = post.data.id;
  detail.hidden = false;
  detailTitle.textContent = post.data.title;
  detailBody.textContent = post.data.body;
  detailAuthor.textContent = post.data.author ?? "작성자 없음";
  comments.replaceChildren();
  for (const comment of commentPage.data) {
    const item = document.createElement("li");
    item.textContent = `${comment.author ?? "작성자 없음"}: ${comment.body}`;
    comments.append(item);
  }
}

required<HTMLFormElement>("#login").addEventListener("submit", (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget as HTMLFormElement);
  void requestJson<TokenResponse>(loginUrl(origin), {
    method: "POST",
    body: { email: form.get("email"), password: form.get("password") }
  })
    .then((data) => {
      state.token = data.token;
      state.name = data.name;
      writeStore(tokenKey, state.token);
      writeStore(nameKey, state.name);
      showSession();
    })
    .catch((error: unknown) => {
      setStatus(error instanceof Error ? error.message : "로그인 실패", true);
    });
});

required<HTMLButtonElement>("#logout").addEventListener("click", () => {
  const finish = (): void => {
    state.token = "";
    state.name = "";
    writeStore(tokenKey, "");
    writeStore(nameKey, "");
    showSession();
  };
  if (!state.token) {
    finish();
    return;
  }
  void requestJson<null>(logoutUrl(origin), { method: "POST", token: state.token, body: {} }).then(finish, finish);
});

required<HTMLFormElement>("#search").addEventListener("submit", (event) => {
  event.preventDefault();
  state.q = String(new FormData(event.currentTarget as HTMLFormElement).get("q") || "");
  state.page = 1;
  void loadPosts().catch((error: unknown) => setStatus(error instanceof Error ? error.message : "검색 실패", true));
});

prev.addEventListener("click", () => {
  state.page -= 1;
  void loadPosts();
});

next.addEventListener("click", () => {
  state.page += 1;
  void loadPosts();
});

required<HTMLFormElement>("#new-post").addEventListener("submit", (event) => {
  event.preventDefault();
  const form = event.currentTarget as HTMLFormElement;
  const data = new FormData(form);
  void requestJson<Resource<Post>>(postsUrl(origin, { page: 1, per: state.per }), {
    method: "POST",
    token: state.token,
    body: { title: data.get("title"), body: data.get("body") }
  })
    .then(async () => {
      form.reset();
      state.page = 1;
      await loadPosts();
    })
    .catch((error: unknown) => {
      setStatus(error instanceof Error ? error.message : "등록 실패", true);
    });
});

required<HTMLFormElement>("#new-comment").addEventListener("submit", (event) => {
  event.preventDefault();
  if (!state.postId) return;
  const form = event.currentTarget as HTMLFormElement;
  const postId = state.postId;
  void requestJson<Resource<Comment>>(commentsUrl(origin, postId), {
    method: "POST",
    token: state.token,
    body: { body: new FormData(form).get("body") }
  })
    .then(async () => {
      form.reset();
      await openPost(postId);
    })
    .catch((error: unknown) => {
      setStatus(error instanceof Error ? error.message : "댓글 실패", true);
    });
});

showSession();
void loadPosts().catch((error: unknown) => setStatus(error instanceof Error ? error.message : "목록 실패", true));

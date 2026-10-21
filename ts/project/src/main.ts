import {
  loginUrl,
  logoutUrl,
  noteUrl,
  notesUrl,
  requestJson,
  tagsUrl,
  type Note,
  type Page,
  type Resource,
  type Tag,
  type TokenResponse
} from "./api";

const origin = "http://127.0.0.1:8001";
const tokenKey = "laravel.project.ts.token";
const nameKey = "laravel.project.ts.name";
const state = {
  token: readStore(tokenKey),
  name: readStore(nameKey),
  page: 1,
  per: 5,
  q: "",
  tag: ""
};

const status = required<HTMLElement>("#status");
const notes = required<HTMLElement>("#notes");
const tags = required<HTMLElement>("#tags");
const meta = required<HTMLElement>("#meta");
const detail = required<HTMLElement>("#detail");
const detailTitle = required<HTMLElement>("#detail-title");
const detailBody = required<HTMLElement>("#detail-body");
const detailAuthor = required<HTMLElement>("#detail-author");
const detailTags = required<HTMLElement>("#detail-tags");
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
  setStatus(state.token ? `${state.name} 로그인` : "로그인 전입니다. 노트는 볼 수 있습니다.");
}

function fail(error: unknown, fallback: string): void {
  setStatus(error instanceof Error ? error.message : fallback, true);
}

async function loadTags(): Promise<void> {
  const data = await requestJson<Resource<Tag[]>>(tagsUrl(origin));
  tags.replaceChildren();
  for (const tag of data.data) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "chip";
    button.textContent = `${tag.name} ${tag.notes_count}`;
    button.addEventListener("click", () => {
      state.tag = tag.name;
      state.page = 1;
      void loadNotes().catch((error: unknown) => fail(error, "목록 실패"));
    });
    tags.append(button);
  }
}

async function loadNotes(): Promise<void> {
  const data = await requestJson<Page<Note>>(notesUrl(origin, state));
  notes.replaceChildren();
  for (const note of data.data) {
    const article = document.createElement("article");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "link";
    button.textContent = note.title;
    button.addEventListener("click", () => {
      void openNote(note.id);
    });
    const line = document.createElement("p");
    line.className = "muted";
    line.textContent = `${note.author ?? "작성자 없음"} · ${note.tags.join(", ")}`;
    article.append(button, line);
    notes.append(article);
  }
  meta.textContent = `${data.meta.total}건 · ${data.meta.current_page} / ${data.meta.last_page}`;
  prev.disabled = data.meta.current_page <= 1;
  next.disabled = data.meta.current_page >= data.meta.last_page;
}

async function openNote(id: number): Promise<void> {
  const note = await requestJson<Resource<Note>>(noteUrl(origin, id));
  detail.hidden = false;
  detailTitle.textContent = note.data.title;
  detailBody.textContent = note.data.body;
  detailAuthor.textContent = note.data.author ?? "작성자 없음";
  detailTags.textContent = note.data.tags.join(", ");
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
    .catch((error: unknown) => fail(error, "로그인 실패"));
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
  const form = new FormData(event.currentTarget as HTMLFormElement);
  state.q = String(form.get("q") || "");
  state.tag = String(form.get("tag") || "");
  state.page = 1;
  void loadNotes().catch((error: unknown) => fail(error, "검색 실패"));
});

prev.addEventListener("click", () => {
  state.page -= 1;
  void loadNotes();
});

next.addEventListener("click", () => {
  state.page += 1;
  void loadNotes();
});

required<HTMLFormElement>("#new-note").addEventListener("submit", (event) => {
  event.preventDefault();
  const form = event.currentTarget as HTMLFormElement;
  const data = new FormData(form);
  void requestJson<Resource<Note>>(notesUrl(origin, { page: 1, per: state.per }), {
    method: "POST",
    token: state.token,
    body: { title: data.get("title"), body: data.get("body"), tags: data.get("tags") || "" }
  })
    .then(async () => {
      form.reset();
      state.page = 1;
      await loadTags();
      await loadNotes();
    })
    .catch((error: unknown) => fail(error, "저장 실패"));
});

showSession();
void Promise.all([loadTags(), loadNotes()]).catch((error: unknown) => fail(error, "목록 실패"));

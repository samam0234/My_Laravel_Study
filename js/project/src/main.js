import { loginUrl, logoutUrl, noteUrl, notesUrl, requestJson, tagsUrl } from "./api.js";

const origin = "http://127.0.0.1:8001";
const tokenKey = "laravel.project.token";
const nameKey = "laravel.project.name";
const state = {
  token: readStore(tokenKey),
  name: readStore(nameKey),
  page: 1,
  per: 5,
  q: "",
  tag: ""
};

const status = document.querySelector("#status");
const notes = document.querySelector("#notes");
const tags = document.querySelector("#tags");
const meta = document.querySelector("#meta");
const detail = document.querySelector("#detail");
const detailTitle = document.querySelector("#detail-title");
const detailBody = document.querySelector("#detail-body");
const detailAuthor = document.querySelector("#detail-author");
const detailTags = document.querySelector("#detail-tags");
const prev = document.querySelector("#prev");
const next = document.querySelector("#next");

function readStore(key) {
  try {
    return sessionStorage.getItem(key) || "";
  } catch {
    return "";
  }
}

function writeStore(key, value) {
  try {
    if (value) sessionStorage.setItem(key, value);
    else sessionStorage.removeItem(key);
  } catch {
    // 저장소를 못 쓰면 메모리 상태만 유지한다.
  }
}

function setStatus(text, isError = false) {
  status.textContent = text;
  status.classList.toggle("error", isError);
}

function showSession() {
  setStatus(state.token ? `${state.name} 로그인` : "로그인 전입니다. 노트는 볼 수 있습니다.");
}

async function loadTags() {
  const data = await requestJson(tagsUrl(origin));
  tags.replaceChildren();
  for (const tag of data.data) {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "chip";
    button.textContent = `${tag.name} ${tag.notes_count}`;
    button.addEventListener("click", () => {
      state.tag = tag.name;
      state.page = 1;
      loadNotes().catch((error) => setStatus(error.message, true));
    });
    tags.append(button);
  }
}

async function loadNotes() {
  const data = await requestJson(notesUrl(origin, state));
  notes.replaceChildren();
  for (const note of data.data) {
    const article = document.createElement("article");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "link";
    button.textContent = note.title;
    button.addEventListener("click", () => openNote(note.id));
    const line = document.createElement("p");
    line.className = "muted";
    line.textContent = `${note.author ?? "작성자 없음"} · ${(note.tags || []).join(", ")}`;
    article.append(button, line);
    notes.append(article);
  }
  meta.textContent = `${data.meta.total}건 · ${data.meta.current_page} / ${data.meta.last_page}`;
  prev.disabled = data.meta.current_page <= 1;
  next.disabled = data.meta.current_page >= data.meta.last_page;
}

async function openNote(id) {
  const note = await requestJson(noteUrl(origin, id));
  detail.hidden = false;
  detailTitle.textContent = note.data.title;
  detailBody.textContent = note.data.body;
  detailAuthor.textContent = note.data.author ?? "작성자 없음";
  detailTags.textContent = (note.data.tags || []).join(", ");
}

document.querySelector("#login").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  try {
    const data = await requestJson(loginUrl(origin), {
      method: "POST",
      body: { email: form.get("email"), password: form.get("password") }
    });
    state.token = data.token;
    state.name = data.name;
    writeStore(tokenKey, state.token);
    writeStore(nameKey, state.name);
    showSession();
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.querySelector("#logout").addEventListener("click", async () => {
  if (state.token) {
    await requestJson(logoutUrl(origin), { method: "POST", token: state.token, body: {} });
  }
  state.token = "";
  state.name = "";
  writeStore(tokenKey, "");
  writeStore(nameKey, "");
  showSession();
});

document.querySelector("#search").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  state.q = form.get("q") || "";
  state.tag = form.get("tag") || "";
  state.page = 1;
  await loadNotes();
});

prev.addEventListener("click", async () => {
  state.page -= 1;
  await loadNotes();
});

next.addEventListener("click", async () => {
  state.page += 1;
  await loadNotes();
});

document.querySelector("#new-note").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = event.currentTarget;
  const data = new FormData(form);
  try {
    await requestJson(notesUrl(origin, { page: 1, per: state.per }), {
      method: "POST",
      token: state.token,
      body: { title: data.get("title"), body: data.get("body"), tags: data.get("tags") || "" }
    });
    form.reset();
    state.page = 1;
    await loadTags();
    await loadNotes();
  } catch (error) {
    setStatus(error.message, true);
  }
});

showSession();
Promise.all([loadTags(), loadNotes()]).catch((error) => setStatus(error.message, true));

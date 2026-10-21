import { commentsUrl, loginUrl, logoutUrl, postUrl, postsUrl, requestJson } from "./api.js";

const origin = "http://127.0.0.1:8000";
const state = {
  token: readStore("laravel.demo.token"),
  name: readStore("laravel.demo.name"),
  page: 1,
  per: 5,
  q: "",
  postId: null
};

const status = document.querySelector("#status");
const posts = document.querySelector("#posts");
const meta = document.querySelector("#meta");
const detail = document.querySelector("#detail");
const detailTitle = document.querySelector("#detail-title");
const detailBody = document.querySelector("#detail-body");
const detailAuthor = document.querySelector("#detail-author");
const comments = document.querySelector("#comments");
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
  setStatus(state.token ? `${state.name} 로그인` : "로그인 전입니다. 목록은 볼 수 있습니다.");
}

async function loadPosts() {
  const data = await requestJson(postsUrl(origin, state));
  posts.replaceChildren();
  for (const post of data.data) {
    const article = document.createElement("article");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "link";
    button.textContent = post.title;
    button.addEventListener("click", () => openPost(post.id));
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

async function openPost(id) {
  const post = await requestJson(postUrl(origin, id));
  const commentPage = await requestJson(commentsUrl(origin, id));
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
    writeStore("laravel.demo.token", state.token);
    writeStore("laravel.demo.name", state.name);
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
  writeStore("laravel.demo.token", "");
  writeStore("laravel.demo.name", "");
  showSession();
});

document.querySelector("#search").addEventListener("submit", async (event) => {
  event.preventDefault();
  state.q = new FormData(event.currentTarget).get("q") || "";
  state.page = 1;
  await loadPosts();
});

prev.addEventListener("click", async () => {
  state.page -= 1;
  await loadPosts();
});

next.addEventListener("click", async () => {
  state.page += 1;
  await loadPosts();
});

document.querySelector("#new-post").addEventListener("submit", async (event) => {
  event.preventDefault();
  const form = new FormData(event.currentTarget);
  try {
    await requestJson(postsUrl(origin, { page: 1, per: state.per }), {
      method: "POST",
      token: state.token,
      body: { title: form.get("title"), body: form.get("body") }
    });
    event.currentTarget.reset();
    state.page = 1;
    await loadPosts();
  } catch (error) {
    setStatus(error.message, true);
  }
});

document.querySelector("#new-comment").addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.postId) return;
  const form = new FormData(event.currentTarget);
  try {
    await requestJson(commentsUrl(origin, state.postId), {
      method: "POST",
      token: state.token,
      body: { body: form.get("body") }
    });
    event.currentTarget.reset();
    await openPost(state.postId);
  } catch (error) {
    setStatus(error.message, true);
  }
});

showSession();
loadPosts().catch((error) => setStatus(error.message, true));

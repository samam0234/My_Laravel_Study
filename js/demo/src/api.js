export function postsUrl(origin, { q = "", page = 1, per = 5 } = {}) {
  const url = new URL("/api/v1/posts", origin);
  if (q) url.searchParams.set("q", q);
  url.searchParams.set("page", String(page));
  url.searchParams.set("per", String(per));
  return url.toString();
}

export function loginUrl(origin) {
  return new URL("/api/v1/login", origin).toString();
}

export function logoutUrl(origin) {
  return new URL("/api/v1/logout", origin).toString();
}

export function postUrl(origin, id) {
  return new URL(`/api/v1/posts/${id}`, origin).toString();
}

export function commentsUrl(origin, postId) {
  return new URL(`/api/v1/posts/${postId}/comments`, origin).toString();
}

export function errorMessage(data, status) {
  const errors = data && data.errors;
  if (errors && typeof errors === "object") {
    const first = Object.values(errors).flat()[0];
    if (first) return String(first);
  }
  if (data && typeof data.message === "string") return data.message;
  return `HTTP ${status}`;
}

export async function requestJson(url, { method = "GET", token, body } = {}) {
  const headers = { accept: "application/json" };
  if (body !== undefined) headers["content-type"] = "application/json";
  if (token) headers.authorization = `Bearer ${token}`;

  const response = await fetch(url, {
    method,
    headers,
    body: body === undefined ? undefined : JSON.stringify(body)
  });
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  if (!response.ok) {
    const error = new Error(errorMessage(data, response.status));
    error.status = response.status;
    throw error;
  }
  return data;
}

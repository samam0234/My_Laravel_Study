export type Post = {
  id: number;
  title: string;
  body: string;
  author: string | null;
  created_at: string;
};

export type Comment = {
  id: number;
  body: string;
  author: string | null;
  created_at: string;
};

export type PageMeta = {
  current_page: number;
  last_page: number;
  per_page: number;
  total: number;
};

export type Resource<T> = { data: T };

export type Page<T> = { data: T[]; meta: PageMeta };

export type TokenResponse = {
  token: string;
  token_type: string;
  name: string;
};

type Query = { q?: string; page?: number; per?: number };

type RequestOptions = {
  method?: string;
  token?: string;
  body?: unknown;
};

export function postsUrl(origin: string, { q = "", page = 1, per = 5 }: Query = {}): string {
  const url = new URL("/api/v1/posts", origin);
  if (q) url.searchParams.set("q", q);
  url.searchParams.set("page", String(page));
  url.searchParams.set("per", String(per));
  return url.toString();
}

export function loginUrl(origin: string): string {
  return new URL("/api/v1/login", origin).toString();
}

export function logoutUrl(origin: string): string {
  return new URL("/api/v1/logout", origin).toString();
}

export function postUrl(origin: string, id: number): string {
  return new URL(`/api/v1/posts/${id}`, origin).toString();
}

export function commentsUrl(origin: string, postId: number): string {
  return new URL(`/api/v1/posts/${postId}/comments`, origin).toString();
}

export function errorMessage(data: unknown, status: number): string {
  if (data && typeof data === "object" && "errors" in data && data.errors && typeof data.errors === "object") {
    const first = Object.values(data.errors as Record<string, unknown[]>).flat()[0];
    if (first) return String(first);
  }
  if (data && typeof data === "object" && "message" in data && typeof data.message === "string") {
    return data.message;
  }
  return `HTTP ${status}`;
}

export async function requestJson<T>(url: string, options: RequestOptions = {}): Promise<T> {
  const headers: Record<string, string> = { accept: "application/json" };
  if (options.body !== undefined) headers["content-type"] = "application/json";
  if (options.token) headers.authorization = `Bearer ${options.token}`;

  const response = await fetch(url, {
    method: options.method ?? "GET",
    headers,
    body: options.body === undefined ? undefined : JSON.stringify(options.body)
  });
  const text = await response.text();
  const data: unknown = text ? JSON.parse(text) : null;
  if (!response.ok) {
    const error = new Error(errorMessage(data, response.status));
    throw error;
  }
  return data as T;
}

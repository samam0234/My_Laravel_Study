import { afterEach, describe, expect, it, vi } from "vitest";
import { commentsUrl, errorMessage, loginUrl, logoutUrl, postsUrl, requestJson } from "./api";

describe("api", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("keeps search, page, and per", () => {
    expect(postsUrl("http://127.0.0.1:8000", { q: "쿠키", page: 2, per: 5 })).toBe(
      "http://127.0.0.1:8000/api/v1/posts?q=%EC%BF%A0%ED%82%A4&page=2&per=5"
    );
  });

  it("points login, logout, and comments at the api", () => {
    expect(loginUrl("http://127.0.0.1:8000")).toBe("http://127.0.0.1:8000/api/v1/login");
    expect(logoutUrl("http://127.0.0.1:8000")).toBe("http://127.0.0.1:8000/api/v1/logout");
    expect(commentsUrl("http://127.0.0.1:8000", 3)).toBe("http://127.0.0.1:8000/api/v1/posts/3/comments");
  });

  it("prefers the first validation error", () => {
    expect(
      errorMessage(
        { message: "The given data was invalid.", errors: { email: ["이메일 또는 비밀번호가 올바르지 않습니다."] } },
        422
      )
    ).toBe("이메일 또는 비밀번호가 올바르지 않습니다.");
  });

  it("sends a bearer token", async () => {
    const fetchMock = vi.fn(async (_url: string, _options?: RequestInit) => {
      return new Response(JSON.stringify({ token: "abc" }), { status: 200 });
    });
    vi.stubGlobal("fetch", fetchMock);
    await requestJson("http://127.0.0.1:8000/api/v1/posts", {
      method: "POST",
      token: "abc",
      body: { title: "제목", body: "본문" }
    });
    const options = fetchMock.mock.calls[0]?.[1];
    expect((options?.headers as Record<string, string>).authorization).toBe("Bearer abc");
  });
});

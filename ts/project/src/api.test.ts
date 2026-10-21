import { afterEach, describe, expect, it, vi } from "vitest";
import { errorMessage, loginUrl, notesUrl, requestJson, tagsUrl } from "./api";

describe("shelf api", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("keeps search, tag, and page", () => {
    expect(notesUrl("http://127.0.0.1:8001", { q: "스키마", tag: "Eloquent", page: 2, per: 5 })).toBe(
      "http://127.0.0.1:8001/api/v1/notes?q=%EC%8A%A4%ED%82%A4%EB%A7%88&tag=Eloquent&page=2&per=5"
    );
  });

  it("points login and tags at the shelf", () => {
    expect(loginUrl("http://127.0.0.1:8001")).toBe("http://127.0.0.1:8001/api/v1/login");
    expect(tagsUrl("http://127.0.0.1:8001")).toBe("http://127.0.0.1:8001/api/v1/tags");
  });

  it("prefers the first validation error", () => {
    expect(errorMessage({ message: "The given data was invalid.", errors: { title: ["제목을 입력해 주세요."] } }, 422)).toBe(
      "제목을 입력해 주세요."
    );
  });

  it("sends a bearer token", async () => {
    const fetchMock = vi.fn(async (_url: string, _options?: RequestInit) => {
      return new Response(JSON.stringify({ data: { id: 1 } }), { status: 201 });
    });
    vi.stubGlobal("fetch", fetchMock);
    await requestJson("http://127.0.0.1:8001/api/v1/notes", {
      method: "POST",
      token: "shelf-token",
      body: { title: "제목", body: "본문", tags: "서재" }
    });
    const options = fetchMock.mock.calls[0]?.[1];
    expect((options?.headers as Record<string, string>).authorization).toBe("Bearer shelf-token");
  });
});

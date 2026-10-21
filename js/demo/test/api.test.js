import assert from "node:assert/strict";
import test from "node:test";
import { commentsUrl, errorMessage, loginUrl, postsUrl } from "../src/api.js";

test("posts url keeps search and page", () => {
  assert.equal(
    postsUrl("http://127.0.0.1:8000", { q: "쿠키", page: 2, per: 5 }),
    "http://127.0.0.1:8000/api/v1/posts?q=%EC%BF%A0%ED%82%A4&page=2&per=5"
  );
});

test("login and comments urls", () => {
  assert.equal(loginUrl("http://127.0.0.1:8000"), "http://127.0.0.1:8000/api/v1/login");
  assert.equal(commentsUrl("http://127.0.0.1:8000", 3), "http://127.0.0.1:8000/api/v1/posts/3/comments");
});

test("validation errors win over the generic message", () => {
  assert.equal(
    errorMessage({ message: "The given data was invalid.", errors: { email: ["이메일 또는 비밀번호가 올바르지 않습니다."] } }, 422),
    "이메일 또는 비밀번호가 올바르지 않습니다."
  );
});

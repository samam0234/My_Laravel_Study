import assert from "node:assert/strict";
import test from "node:test";
import { errorMessage, loginUrl, notesUrl, tagsUrl } from "../src/api.js";

test("notes url keeps search, tag, and page", () => {
  assert.equal(
    notesUrl("http://127.0.0.1:8001", { q: "스키마", tag: "Eloquent", page: 2, per: 5 }),
    "http://127.0.0.1:8001/api/v1/notes?q=%EC%8A%A4%ED%82%A4%EB%A7%88&tag=Eloquent&page=2&per=5"
  );
});

test("login and tags urls", () => {
  assert.equal(loginUrl("http://127.0.0.1:8001"), "http://127.0.0.1:8001/api/v1/login");
  assert.equal(tagsUrl("http://127.0.0.1:8001"), "http://127.0.0.1:8001/api/v1/tags");
});

test("validation errors win over the generic message", () => {
  assert.equal(
    errorMessage({ message: "The given data was invalid.", errors: { title: ["제목을 입력해 주세요."] } }, 422),
    "제목을 입력해 주세요."
  );
});

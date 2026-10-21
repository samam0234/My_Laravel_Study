<?php

namespace App\Http\Controllers;

use App\Models\Note;
use App\Models\Tag;
use Illuminate\Http\Request;

class NoteController extends Controller
{
    public function index(Request $request)
    {
        $this->authorize('viewAny', Note::class);

        $notes = Note::query()
            ->with(['user', 'tags'])
            ->search($request->query('q'))
            ->tagged($request->query('tag'))
            ->latest('id')
            ->paginate(5)
            ->withQueryString();

        return view('notes.index', [
            'notes' => $notes,
            'tags' => Tag::query()->orderBy('name')->get(),
        ]);
    }

    public function create()
    {
        return view('notes.create');
    }

    public function store(Request $request)
    {
        $data = $this->validated($request);
        $note = $request->user()->notes()->create($data);
        $note->syncTagString($request->input('tags'));

        return redirect()
            ->route('notes.show', $note)
            ->with('status', '노트를 저장했습니다.');
    }

    public function show(Note $note)
    {
        $this->authorize('view', $note);
        $note->load(['user', 'tags']);

        return view('notes.show', ['note' => $note]);
    }

    public function edit(Note $note)
    {
        $this->authorize('update', $note);
        $note->load('tags');

        return view('notes.edit', ['note' => $note]);
    }

    public function update(Request $request, Note $note)
    {
        $this->authorize('update', $note);
        $note->update($this->validated($request));
        $note->syncTagString($request->input('tags'));

        return redirect()
            ->route('notes.show', $note)
            ->with('status', '노트를 수정했습니다.');
    }

    public function destroy(Note $note)
    {
        $this->authorize('delete', $note);
        $note->delete();

        return redirect()
            ->route('notes.index')
            ->with('status', '노트를 삭제했습니다.');
    }

    /**
     * @return array{title: string, body: string}
     */
    private function validated(Request $request): array
    {
        return $request->validate([
            'title' => ['required', 'string', 'max:120'],
            'body' => ['required', 'string'],
            'tags' => ['nullable', 'string', 'max:200'],
        ], [
            'title.required' => '제목을 입력해 주세요.',
            'body.required' => '내용을 입력해 주세요.',
        ]);
    }
}

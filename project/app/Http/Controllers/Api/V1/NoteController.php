<?php

namespace App\Http\Controllers\Api\V1;

use App\Http\Controllers\Controller;
use App\Http\Resources\NoteResource;
use App\Models\Note;
use Illuminate\Http\Request;

class NoteController extends Controller
{
    public function index(Request $request)
    {
        $this->authorize('viewAny', Note::class);

        $perPage = min(max($request->integer('per', 10), 1), 50);
        $notes = Note::query()
            ->with(['user', 'tags'])
            ->search($request->query('q'))
            ->tagged($request->query('tag'))
            ->latest('id')
            ->paginate($perPage)
            ->withQueryString();

        return NoteResource::collection($notes);
    }

    public function store(Request $request)
    {
        $data = $this->validated($request);
        $note = $request->user()->notes()->create($data);
        $note->syncTagString($request->input('tags'));

        return (new NoteResource($note->load(['user', 'tags'])))
            ->response()
            ->setStatusCode(201);
    }

    public function show(Note $note)
    {
        $this->authorize('view', $note);

        return new NoteResource($note->load(['user', 'tags']));
    }

    public function update(Request $request, Note $note)
    {
        $this->authorize('update', $note);
        $note->update($this->validated($request));
        $note->syncTagString($request->input('tags'));

        return new NoteResource($note->load(['user', 'tags']));
    }

    public function destroy(Note $note)
    {
        $this->authorize('delete', $note);
        $note->delete();

        return response()->noContent();
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

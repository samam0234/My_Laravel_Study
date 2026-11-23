<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Resources\EntryResource;
use App\Services\LibraryStats;
use App\Support\TagNames;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Gate;
use Symfony\Component\HttpFoundation\Response;

class ContractController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        $request->validate(['q' => ['nullable', 'string', 'max:200'], 'page' => ['sometimes', 'integer', 'min:1'],
            'limit' => ['sometimes', 'integer', 'min:1'], 'sort' => ['sometimes', 'in:createdAt,-createdAt,-commentCount']]);
        $query = config('study.model')::query()->with(['user'])->search($request->query('q'));
        $query->withCount('comments');
        $sort = $request->query('sort', '-createdAt');
        if ($sort === '-commentCount') {
            $query->orderByDesc('comments_count');
        } else {
            $query->orderBy('created_at', $sort === 'createdAt' ? 'asc' : 'desc');
        }
        $items = $query->orderBy('id', $sort === 'createdAt' ? 'asc' : 'desc')
            ->paginate(min($request->integer('limit', 10), 50));

        return response()->json(['data' => EntryResource::collection($items)->resolve($request), 'meta' => [
            'page' => $items->currentPage(), 'limit' => $items->perPage(), 'total' => $items->total(),
            'totalPages' => $items->lastPage(), 'q' => $request->query('q', ''),
        ]]);
    }

    public function show(int $id): EntryResource
    {
        return new EntryResource(config('study.model')::query()->with(['user'])->withCount('comments')->findOrFail($id));
    }

    public function store(Request $request): JsonResponse
    {
        $data = $this->validated($request);
        if (isset($data['tags'])) {
            $data['tags'] = TagNames::normalize($data['tags']);
        }
        $entry = DB::transaction(function () use ($request, $data) {
            $relation = config('study.relation');
            $entry = $request->user()->{$relation}()->create($data);

            return $entry;
        });
        app(LibraryStats::class)->invalidate();

        return (new EntryResource($entry->load(['user'])))->response()->setStatusCode(201)
            ->header('Location', '/api/posts/'.$entry->id);
    }

    public function update(Request $request, int $id): EntryResource
    {
        $entry = config('study.model')::query()->findOrFail($id);
        Gate::authorize('update', $entry);
        $data = $this->validated($request, true);
        if (isset($data['tags'])) {
            $data['tags'] = TagNames::normalize($data['tags']);
        }
        DB::transaction(function () use ($entry, $data): void {
            $entry->update($data);

        });

        return new EntryResource($entry->load(['user'])->loadCount('comments'));
    }

    public function destroy(int $id): Response
    {
        $entry = config('study.model')::query()->findOrFail($id);
        Gate::authorize('delete', $entry);
        $entry->delete();
        app(LibraryStats::class)->invalidate();

        return response()->noContent();
    }

    private function validated(Request $request, bool $partial = false): array
    {
        return $request->validate([
            'title' => [$partial ? 'sometimes' : 'required', 'required', 'string', 'max:200'],
            'body' => [$partial ? 'sometimes' : 'required', 'required', 'string', 'max:20000'],
            'tags' => ['sometimes', 'array', 'max:8'], 'tags.*' => ['required', 'string', 'max:30', 'distinct'],
        ]);
    }
}

<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
use App\Http\Resources\DocumentResource;
use App\Jobs\SummarizeDocument;
use App\Models\Document;
use App\Services\DocumentAi;
use Illuminate\Http\JsonResponse;
use Illuminate\Http\Request;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Storage;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\HttpFoundation\StreamedResponse;
use Throwable;

class DocumentController extends Controller
{
    public function index(Request $request): JsonResponse
    {
        return response()->json(['data' => DocumentResource::collection(Document::query()->where('user_id', $request->user()->id)->latest('id')->limit(50)->get())->resolve($request)]);
    }

    public function store(Request $request): JsonResponse
    {
        $request->validate(['file' => ['required', 'file', 'max:100', 'extensions:txt,md', 'mimetypes:text/plain,text/markdown,text/x-markdown']]);
        $file = $request->file('file');
        $content = $file->getContent();
        abort_unless(mb_check_encoding($content, 'UTF-8') && ! str_contains($content, "\0"), 422);
        $path = $file->store('documents', 'local');
        try {
            $document = Document::query()->create(['user_id' => $request->user()->id,
                'filename' => basename($file->getClientOriginalName()), 'path' => $path, 'content' => $content]);
        } catch (Throwable $exception) {
            Storage::disk('local')->delete($path);
            throw $exception;
        }
        SummarizeDocument::dispatch($document->id);

        return response()->json(['data' => (new DocumentResource($document->fresh()))->resolve($request)], 202);
    }

    public function download(Request $request, Document $document): StreamedResponse
    {
        $this->owned($request, $document);

        return Storage::disk('local')->download($document->path, $document->filename, ['Content-Type' => 'text/plain; charset=utf-8', 'X-Content-Type-Options' => 'nosniff']);
    }

    public function destroy(Request $request, Document $document): Response
    {
        $this->owned($request, $document);
        Storage::disk('local')->delete($document->path);
        $document->delete();

        return response()->noContent();
    }

    public function history(Request $request, Document $document): JsonResponse
    {
        $this->owned($request, $document);

        $questions = DB::table('document_questions')->where('document_id', $document->id)->latest('id')->limit(20)->get();

        return response()->json(['data' => $questions->map(fn ($row) => ['id' => $row->id, 'documentId' => $row->document_id,
            'question' => $row->question, 'answer' => $row->answer, 'sources' => json_decode($row->sources, true),
            'createdAt' => Carbon::parse($row->created_at)->utc()->toISOString()])]);
    }

    public function ask(Request $request, Document $document, DocumentAi $ai): StreamedResponse
    {
        $this->owned($request, $document);
        $data = $request->validate(['question' => ['required', 'string', 'max:1000']]);
        $sources = $ai->excerpts($document->content, $data['question']);
        $context = implode("\n", array_map(fn ($source) => '(발췌 '.$source['index'].') '.$source['text'], $sources));

        return response()->stream(function () use ($ai, $context, $data, $sources, $document): void {
            $emit = function (array $event): void {
                echo 'data: '.json_encode($event, JSON_UNESCAPED_UNICODE)."\n\n";
                if (ob_get_level() > 0) {
                    ob_flush();
                } flush();
            };
            $answer = '';
            try {
                foreach ($ai->stream($context, $data['question']) as $delta) {
                    $answer .= $delta;
                    $emit(['delta' => $delta]);
                    if (connection_aborted()) {
                        return;
                    }
                }
                DB::table('document_questions')->insert(['document_id' => $document->id, 'question' => $data['question'],
                    'answer' => $answer, 'sources' => json_encode($sources, JSON_UNESCAPED_UNICODE), 'created_at' => now(), 'updated_at' => now()]);
                $emit(['done' => true, 'sources' => $sources, 'driver' => config('study.ai_driver')]);
            } catch (Throwable $exception) {
                report($exception);
                $emit(['error' => 'AI 서비스 연결을 확인하세요.']);
            }
        }, 200, ['Content-Type' => 'text/event-stream', 'Cache-Control' => 'no-cache', 'X-Accel-Buffering' => 'no']);
    }

    private function owned(Request $request, Document $document): void
    {
        abort_unless($document->user_id === $request->user()->id, 404);
    }
}

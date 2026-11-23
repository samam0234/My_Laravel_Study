<?php

namespace App\Jobs;

use App\Models\Document;
use App\Notifications\DocumentReady;
use App\Services\DocumentAi;
use Illuminate\Contracts\Queue\ShouldBeUnique;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Queue\Queueable;
use Throwable;

class SummarizeDocument implements ShouldBeUnique, ShouldQueue
{
    use Queueable;

    public int $tries = 3;

    public int $timeout = 100;

    public int $uniqueFor = 180;

    public function uniqueId(): string
    {
        return (string) $this->documentId;
    }

    public function __construct(public int $documentId) {}

    public function backoff(): array
    {
        return [10, 30, 60];
    }

    public function handle(DocumentAi $ai): void
    {
        $document = Document::query()->find($this->documentId);
        if (! $document || $document->status === 'ready') {
            return;
        }
        $document->update(['status' => 'processing']);
        $summary = $ai->summarize($document->content);
        $document->update(['summary' => $summary, 'status' => 'ready']);
        $document->user->notify(new DocumentReady($document->id));
    }

    public function failed(?Throwable $exception): void
    {
        Document::query()->whereKey($this->documentId)->update(['status' => 'failed']);
    }
}

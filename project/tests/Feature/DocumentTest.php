<?php

namespace Tests\Feature;

use App\Jobs\SummarizeDocument;
use App\Models\Document;
use App\Models\User;
use App\Notifications\DocumentReady;
use App\Services\DocumentAi;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Illuminate\Http\UploadedFile;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Notification;
use Illuminate\Support\Facades\Queue;
use Illuminate\Support\Facades\Storage;
use Tests\TestCase;

class DocumentTest extends TestCase
{
    use RefreshDatabase;

    public function test_upload_returns_202_stores_private_file_and_queues_owner_document(): void
    {
        $user = User::factory()->create();
        Storage::fake('local');
        Queue::fake([SummarizeDocument::class]);
        $this->withToken($user->createToken('test')->plainTextToken)->post('/api/documents', ['file' => UploadedFile::fake()->createWithContent('study.txt', 'Laravel 문서 요약 연습입니다.')], ['Accept' => 'application/json'])
            ->assertAccepted()->assertJsonPath('data.userId', $user->id)->assertJsonMissingPath('data.content')->assertJsonMissingPath('data.path');
        $document = Document::query()->firstOrFail();
        Storage::disk('local')->assertExists($document->path);
        Queue::assertPushed(SummarizeDocument::class, fn ($job) => $job->documentId === $document->id);
        $this->assertDatabaseHas('documents', ['id' => $document->id, 'status' => 'queued']);
    }

    public function test_unsupported_file_returns_400_and_does_not_dispatch(): void
    {
        $user = User::factory()->create();
        Storage::fake('local');
        Queue::fake([SummarizeDocument::class]);
        $this->withToken($user->createToken('test')->plainTextToken)->post('/api/documents', ['file' => UploadedFile::fake()->createWithContent('attack.php', '<?php echo 1;')], ['Accept' => 'application/json'])->assertBadRequest();
        $this->assertDatabaseCount('documents', 0);
        Queue::assertNotPushed(SummarizeDocument::class);
    }

    public function test_foreign_document_is_hidden_from_list_download_delete_and_ask(): void
    {
        $document = Document::factory()->create();
        $other = User::factory()->create();
        $this->withToken($other->createToken('test')->plainTextToken)->getJson('/api/documents')->assertOk()->assertJsonCount(0, 'data');
        $this->getJson('/api/documents/'.$document->id.'/download')->assertNotFound();
        $this->deleteJson('/api/documents/'.$document->id)->assertNotFound();
        $this->postJson('/api/documents/'.$document->id.'/ask', ['question' => '문서'])->assertNotFound();
        $this->assertModelExists($document);
    }

    public function test_summary_job_persists_summary_and_sends_notification_once(): void
    {
        $document = Document::factory()->create();
        Notification::fake();
        config(['study.ai_driver' => 'mock']);
        $job = new SummarizeDocument($document->id);
        $job->handle(app(DocumentAi::class));
        $job->handle(app(DocumentAi::class));
        $this->assertDatabaseHas('documents', ['id' => $document->id, 'status' => 'ready']);
        $this->assertStringContainsString('[mock 실습]', $document->fresh()->summary);
        Notification::assertSentToTimes($document->user, DocumentReady::class, 1);
    }

    public function test_ask_streams_deltas_and_saves_grounded_history(): void
    {
        $document = Document::factory()->create();
        config(['study.ai_driver' => 'mock']);
        $response = $this->withToken($document->user->createToken('test')->plainTextToken)->postJson('/api/documents/'.$document->id.'/ask', ['question' => 'Laravel 문서']);
        $response->assertOk()->assertHeader('Content-Type', 'text/event-stream; charset=UTF-8');
        $stream = $response->streamedContent();
        $this->assertStringContainsString('"done":true', $stream);
        $this->assertStringContainsString('"delta":', $stream);
        $this->assertDatabaseHas('document_questions', ['document_id' => $document->id, 'question' => 'Laravel 문서']);
    }

    public function test_ollama_ndjson_stream_is_relayed_without_network(): void
    {
        config(['study.ai_driver' => 'ollama', 'study.ai_url' => 'http://ollama.test']);
        Http::preventStrayRequests();
        Http::fake(['http://ollama.test/api/chat' => Http::response("{\"message\":{\"content\":\"첫 토큰\"},\"done\":false}\n{\"message\":{\"content\":\" 끝\"},\"done\":true}\n", 200)]);
        $answer = implode('', iterator_to_array(app(DocumentAi::class)->stream('근거', '질문')));
        $this->assertSame('첫 토큰 끝', $answer);
        Http::assertSent(fn ($request) => $request['stream'] === true && $request['messages'][0]['role'] === 'system');
    }

    public function test_ollama_disconnect_emits_error_and_does_not_store_partial_answer(): void
    {
        $document = Document::factory()->create();
        config(['study.ai_driver' => 'ollama', 'study.ai_url' => 'http://ollama.test']);
        Http::preventStrayRequests();
        Http::fake(['http://ollama.test/api/chat' => Http::response('offline', 503)]);
        $response = $this->withToken($document->user->createToken('test')->plainTextToken)->postJson('/api/documents/'.$document->id.'/ask', ['question' => 'Laravel']);
        $response->assertOk();
        $this->assertStringContainsString('"error":', $response->streamedContent());
        $this->assertDatabaseCount('document_questions', 0);
        Http::assertSentCount(1);
    }

    public function test_mcp_requires_auth_and_hides_foreign_document(): void
    {
        $document = Document::factory()->create();
        $other = User::factory()->create();
        $payload = ['jsonrpc' => '2.0', 'id' => 1, 'method' => 'tools/call', 'params' => ['name' => 'read-document', 'arguments' => ['id' => $document->id]]];
        $this->postJson('/mcp/library', $payload)->assertUnauthorized();
        $this->withToken($other->createToken('mcp')->plainTextToken)->postJson('/mcp/library', $payload)
            ->assertOk()->assertJsonPath('result.isError', true)->assertJsonPath('result.content.0.text', 'Document not found');
        $this->app['auth']->forgetGuards();
        $this->withToken($document->user->createToken('mcp')->plainTextToken)->postJson('/mcp/library', $payload)
            ->assertOk()->assertJsonPath('result.content.0.text', $document->content);
    }
}

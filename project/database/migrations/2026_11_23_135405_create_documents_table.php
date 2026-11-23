<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::create('documents', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('user_id')->constrained()->cascadeOnDelete();
            $table->string('filename');
            $table->string('path');
            $table->longText('content');
            $table->string('status')->default('queued');
            $table->text('summary')->nullable();
            $table->timestamps();
            $table->index(['user_id', 'created_at']);
        });
        Schema::create('document_questions', function (Blueprint $table): void {
            $table->id();
            $table->foreignId('document_id')->constrained()->cascadeOnDelete();
            $table->text('question');
            $table->text('answer');
            $table->json('sources');
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('document_questions');
        Schema::dropIfExists('documents');
    }
};

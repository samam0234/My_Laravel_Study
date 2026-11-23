<?php

namespace App\Notifications;

use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Notifications\Messages\MailMessage;
use Illuminate\Notifications\Notification;

class DocumentReady extends Notification implements ShouldQueue
{
    use Queueable;

    public int $tries = 3;

    public function __construct(public int $documentId) {}

    public function via(object $notifiable): array
    {
        return config('broadcasting.default') === 'reverb' ? ['database', 'mail', 'broadcast'] : ['database', 'mail'];
    }

    public function toMail(object $notifiable): MailMessage
    {
        return (new MailMessage)->subject('문서 요약 완료')->line('문서 요약을 확인할 수 있습니다.')
            ->action('학습 서재', url('/app'));
    }

    public function toArray(object $notifiable): array
    {
        return ['documentId' => $this->documentId, 'message' => '문서 요약이 완료되었습니다.'];
    }
}

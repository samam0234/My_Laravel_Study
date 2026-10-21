@csrf
@if ($errors->any())
    <ul class="errors">
        @foreach ($errors->all() as $error)
            <li>{{ $error }}</li>
        @endforeach
    </ul>
@endif
<label>제목
    <input name="title" value="{{ old('title', $note->title ?? '') }}" maxlength="120" required>
</label>
<label>내용
    <textarea name="body" required>{{ old('body', $note->body ?? '') }}</textarea>
</label>
<label>태그
    <input name="tags" value="{{ old('tags', isset($note) ? $note->tags->pluck('name')->implode(', ') : '') }}" placeholder="쉼표로 구분">
</label>

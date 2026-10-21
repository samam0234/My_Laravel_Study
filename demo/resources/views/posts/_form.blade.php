@csrf
@if ($errors->any())
    <ul class="errors">
        @foreach ($errors->all() as $error)
            <li>{{ $error }}</li>
        @endforeach
    </ul>
@endif
<label>제목
    <input name="title" value="{{ old('title', $post->title ?? '') }}" maxlength="120" required>
</label>
<label>내용
    <textarea name="body" required>{{ old('body', $post->body ?? '') }}</textarea>
</label>

<script>
	import { imageUrl, notesFor, yearLabel } from '#lib/photos.js';
	import NoteCard from '#lib/NoteCard.svelte';

	/** @type {import('./$types').PageProps} */
	let { data } = $props();
	let photo = $derived(data.photo);
	let enhanced = $state(false);
	let notes = $derived(notesFor(photo.id));
	let downloadName = $derived(fileName(photo.caption, photo.id, enhanced));

	/** "Bruer - W.T. & Clara Bruer (enhanced).webp" from the caption's first few words */
	function fileName(caption, id, isEnhanced) {
		const words = caption.replace(/[^\w\s&.,'-]/g, '').split(/\s+/).slice(0, 8).join(' ');
		return `Bruer - ${words || id}${isEnhanced ? ' (enhanced)' : ''}.webp`;
	}

	$effect(() => {
		photo.id;
		enhanced = false;
	});

	/** @param {KeyboardEvent} e */
	function onKey(e) {
		if (e.target instanceof HTMLInputElement) return;
		if (e.key === 'ArrowLeft' && data.prev) location.assign(`/photo/${data.prev}`);
		if (e.key === 'ArrowRight' && data.next) location.assign(`/photo/${data.next}`);
	}
</script>

<svelte:window onkeydown={onKey} />
<svelte:head><title>{photo.caption.slice(0, 60) || 'Photo'} · Bruer Family</title></svelte:head>

<div class="grid gap-8 lg:grid-cols-[minmax(0,3fr)_minmax(0,2fr)]">
	<figure>
		<img
			src={imageUrl(photo.id, enhanced ? 'enhanced' : 'original')}
			alt={photo.caption}
			width={photo.width}
			height={photo.height}
			class="mx-auto h-auto max-h-[80vh] w-auto rounded shadow-md"
		/>
		<div class="mt-3 flex items-center justify-center gap-3">
			{#if photo.enhanced}
				<button
					onclick={() => (enhanced = !enhanced)}
					class="rounded-full border border-sepia px-4 py-1.5 text-sm transition
						{enhanced ? 'bg-sepia text-white' : 'text-sepia hover:bg-sepia/10'}"
				>
					{enhanced ? 'Show original' : '✨ Enhance'}
				</button>
			{/if}
			<a
				href={imageUrl(photo.id, enhanced ? 'enhanced' : 'original')}
				download={downloadName}
				class="rounded-full border border-ink/20 px-4 py-1.5 text-sm text-ink/70 transition hover:bg-ink/5"
			>
				↓ Download {enhanced ? 'enhanced' : 'photo'}
			</a>
		</div>
		{#if enhanced}
			<p class="mt-2 text-center text-xs text-ink/50">
				AI-enhanced: scratches and dust repaired, detail sharpened, contrast restored. Faces are not
				redrawn.
			</p>
		{/if}
	</figure>

	<aside class="space-y-6">
		<div>
			<p class="text-xs font-semibold tracking-wide text-sepia uppercase">Caption</p>
			<p class="mt-2 font-serif text-lg leading-relaxed">{photo.caption || 'No caption'}</p>
			<div class="mt-3 flex flex-wrap gap-2 text-xs">
				{#if photo.year}
					<span class="rounded-full bg-ink/5 px-2.5 py-1 text-ink/70" title={photo.yearIsGuess ? 'Estimated from the caption' : 'From the caption'}>
						{yearLabel(photo)}
					</span>
				{/if}
				{#each photo.families as f (f)}
					<a href="/?family={encodeURIComponent(f)}" class="rounded-full border border-sepia/30 px-2.5 py-1 text-sepia hover:bg-sepia/10">{f}</a>
				{/each}
				{#each photo.topics as t (t)}
					<a href="/?topic={encodeURIComponent(t)}" class="rounded-full bg-sepia/10 px-2.5 py-1 text-sepia hover:bg-sepia/20">{t}</a>
				{/each}
			</div>
		</div>

		{#each notes as note (note.title)}
			<NoteCard {note} currentId={photo.id} />
		{/each}

		<nav class="flex justify-between border-t border-sepia/20 pt-4 text-sm">
			{#if data.prev}<a href="/photo/{data.prev}" class="text-sepia hover:underline">← Previous</a>
			{:else}<span></span>{/if}
			<a href="/" class="text-ink/50 hover:underline">All photos</a>
			{#if data.next}<a href="/photo/{data.next}" class="text-sepia hover:underline">Next →</a>
			{:else}<span></span>{/if}
		</nav>
	</aside>
</div>

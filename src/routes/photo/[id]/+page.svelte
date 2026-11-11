<script>
	import { imageUrl, notesFor } from '#lib/photos.js';
	import NoteCard from '#lib/NoteCard.svelte';

	/** @type {import('./$types').PageProps} */
	let { data } = $props();
	let photo = $derived(data.photo);
	let enhanced = $state(false);
	let notes = $derived(notesFor(photo.id));

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
		{#if photo.enhanced}
			<div class="mt-3 flex items-center justify-center gap-3">
				<button
					onclick={() => (enhanced = !enhanced)}
					class="rounded-full border border-sepia px-4 py-1 text-sm transition
						{enhanced ? 'bg-sepia text-white' : 'text-sepia hover:bg-sepia/10'}"
				>
					{enhanced ? 'Show original' : '✨ Enhance'}
				</button>
				<a
					href={imageUrl(photo.id, enhanced ? 'enhanced' : 'original')}
					download
					class="text-sm text-ink/50 hover:underline">Download</a
				>
			</div>
			{#if enhanced}
				<p class="mt-2 text-center text-xs text-ink/50">
					AI-enhanced: scratches and dust repaired, detail sharpened, contrast restored. Faces are not
					redrawn.
				</p>
			{/if}
		{/if}
	</figure>

	<aside class="space-y-6">
		<div>
			<p class="text-xs font-semibold tracking-wide text-sepia uppercase">Caption</p>
			<p class="mt-2 font-serif text-lg leading-relaxed">{photo.caption || 'No caption'}</p>
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

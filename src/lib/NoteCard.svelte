<script>
	import { imageUrl } from '#lib/photos.js';

	/** @type {{ note: import('#lib/photos.js').Observation, currentId?: string }} */
	let { note, currentId } = $props();
	let isConflict = $derived(note.kind === 'conflict');
	let others = $derived(note.photos.filter((id) => id !== currentId));
</script>

<article class="rounded border-l-4 bg-white/60 p-4 {isConflict ? 'border-conflict' : 'border-sepia'}">
	<p class="text-xs font-semibold tracking-wide uppercase {isConflict ? 'text-conflict' : 'text-sepia'}">
		{isConflict ? "Doesn't add up" : 'Research note'}
	</p>
	<h3 class="mt-1 font-serif text-lg">{note.title}</h3>
	<p class="mt-2 text-sm leading-relaxed text-ink/80">{note.body}</p>

	{#if others.length}
		<div class="mt-3 flex flex-wrap gap-2">
			{#each others as id (id)}
				<a href="/photo/{id}" title="Related photo">
					<img src={imageUrl(id, 'thumb')} alt="" class="h-14 w-14 rounded object-cover" loading="lazy" />
				</a>
			{/each}
		</div>
	{/if}

	{#if note.sources?.length}
		<p class="mt-3 text-xs text-ink/50">
			Sources:
			{#each note.sources as url, i (url)}
				<a href={url} class="underline" target="_blank" rel="noreferrer">{new URL(url).hostname}</a>{i <
				note.sources.length - 1
					? ', '
					: ''}
			{/each}
		</p>
	{/if}
</article>

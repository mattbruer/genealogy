<script>
	import { photos, notes, search, imageUrl, notesFor } from '#lib/photos.js';

	const conflicts = notes.filter((n) => n.kind === 'conflict');
	const patterns = notes.filter((n) => n.kind === 'pattern');

	let query = $state('');
	let results = $derived(search(query));
</script>

<section class="mb-8 max-w-2xl">
	<h1 class="font-serif text-4xl">The Bruers, Fitches, Masseys &amp; Cramers</h1>
	<p class="mt-3 text-ink/70">
		{photos.length} photographs, captioned by Bob Bruer. Open any photo to read its caption,
		research notes, and an AI-enhanced version.
	</p>
	<a
		href="/notes"
		class="mt-6 block rounded-lg border-l-4 border-conflict bg-white p-5 shadow-sm transition hover:shadow-md"
	>
		<p class="text-xs font-semibold tracking-wide text-conflict uppercase">
			Reading all {photos.length} captions together
		</p>
		<p class="mt-1 font-serif text-xl">
			{conflicts.length} things that don't add up, and {patterns.length} patterns hiding across the photos
		</p>
		<p class="mt-2 text-sm text-ink/70">
			A man who was 92 and 93 at once, an address that doesn't fit, a birthplace with three answers,
			and a name that leads to Thomas Jefferson. <span class="font-medium text-conflict">See them all →</span>
		</p>
	</a>
	<input
		type="search"
		bind:value={query}
		placeholder="Search captions: a name, a place, a year…"
		class="mt-6 w-full rounded border border-sepia/30 bg-white px-4 py-2 outline-none focus:border-sepia"
	/>
	{#if query}
		<p class="mt-2 text-sm text-ink/60">{results.length} matching photos</p>
	{/if}
</section>

<div class="columns-2 gap-4 sm:columns-3 lg:columns-4">
	{#each results as photo (photo.id)}
		<a href="/photo/{photo.id}" class="group mb-4 block break-inside-avoid">
			<img
				src={imageUrl(photo.id, 'thumb')}
				alt={photo.caption}
				width={photo.width}
				height={photo.height}
				loading="lazy"
				class="h-auto w-full rounded shadow-sm transition group-hover:shadow-md"
			/>
			<p class="mt-2 line-clamp-2 text-sm text-ink/80">
				{#if notesFor(photo.id).some((n) => n.kind === 'conflict')}
					<span class="mr-1 text-conflict" title="Has a caption conflict">●</span>
				{/if}
				{photo.caption || 'No caption'}
			</p>
		</a>
	{/each}
</div>

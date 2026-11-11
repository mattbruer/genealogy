<script>
	import { onMount } from 'svelte';
	import {
		photos,
		notes,
		families,
		topics,
		filterPhotos,
		groupByDecade,
		imageUrl,
		notesFor,
		yearLabel
	} from '#lib/photos.js';

	const conflicts = notes.filter((n) => n.kind === 'conflict');
	const patterns = notes.filter((n) => n.kind === 'pattern');

	let query = $state('');
	let family = $state('');
	let topic = $state('');
	let order = $state(/** @type {'oldest' | 'newest'} */ ('oldest'));

	let results = $derived(filterPhotos({ query, family, topic, order }));
	let groups = $derived(groupByDecade(results));
	let filtering = $derived(Boolean(query || family || topic));

	// Filters live in the URL so photo pages can link here and Back returns to the same view
	onMount(() => {
		const params = new URLSearchParams(location.search);
		family = params.get('family') ?? '';
		topic = params.get('topic') ?? '';
	});

	$effect(() => {
		const params = new URLSearchParams();
		if (family) params.set('family', family);
		if (topic) params.set('topic', topic);
		history.replaceState(history.state, '', params.size ? `?${params}` : location.pathname);
	});

	function clear() {
		query = family = topic = '';
	}

	const selectClass =
		'rounded border border-sepia/30 bg-white px-3 py-2 text-sm outline-none focus:border-sepia';
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
</section>

<section class="sticky top-0 z-10 -mx-4 mb-6 border-b border-sepia/20 bg-paper/95 px-4 py-3 backdrop-blur">
	<div class="flex flex-wrap items-center gap-2">
		<input
			type="search"
			bind:value={query}
			placeholder="Search captions…"
			class="{selectClass} min-w-48 flex-1"
		/>
		<select bind:value={family} class={selectClass} aria-label="Family branch">
			<option value="">All families</option>
			{#each families as f (f.name)}<option value={f.name}>{f.name} ({f.count})</option>{/each}
		</select>
		<select bind:value={topic} class={selectClass} aria-label="Topic">
			<option value="">All topics</option>
			{#each topics as t (t.name)}<option value={t.name}>{t.name} ({t.count})</option>{/each}
		</select>
		<select bind:value={order} class={selectClass} aria-label="Order">
			<option value="oldest">Oldest first</option>
			<option value="newest">Newest first</option>
		</select>
	</div>
	<nav class="mt-2 flex flex-wrap gap-x-3 gap-y-1 text-sm text-ink/60">
		{#if filtering}
			<span>{results.length} photos</span>
			<button onclick={clear} class="text-sepia hover:underline">Clear filters</button>
			<span class="text-ink/30">·</span>
		{/if}
		{#each groups as g (g.label)}
			<a href="#{g.label}" class="hover:text-sepia hover:underline">{g.label}</a>
		{/each}
	</nav>
</section>

{#each groups as group (group.label)}
	<section id={group.label} class="mb-10 scroll-mt-28">
		<h2 class="mb-4 flex items-baseline gap-3 font-serif text-2xl">
			{group.label}
			<span class="font-sans text-sm text-ink/50">{group.photos.length} photos</span>
		</h2>
		<div class="columns-2 gap-4 sm:columns-3 lg:columns-4">
			{#each group.photos as photo (photo.id)}
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
						{#if photo.year}<span class="text-ink/50">{yearLabel(photo)} · </span>{/if}
						{photo.caption || 'No caption'}
					</p>
				</a>
			{/each}
		</div>
	</section>
{:else}
	<p class="text-ink/60">No photos match. <button onclick={clear} class="text-sepia underline">Clear filters</button></p>
{/each}

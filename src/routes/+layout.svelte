<script>
	import '../app.css';
	import { notes } from '#lib/photos.js';

	const conflictCount = notes.filter((n) => n.kind === 'conflict').length;

	/** @type {{children: import('svelte').Snippet}} */
	let { children } = $props();
</script>

<svelte:head>
	<title>Bruer Family Photographs</title>
	<link rel="preconnect" href="https://fonts.googleapis.com" />
	<link
		rel="stylesheet"
		href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Libre+Caslon+Text:ital,wght@0,400;0,700;1,400&display=swap"
	/>
</svelte:head>

<header class="border-b border-sepia/20">
	<nav class="mx-auto flex max-w-7xl items-baseline justify-between gap-4 px-4 py-4">
		<a href="/" class="font-serif text-xl">Bruer Family Photographs</a>
		<a
			href="/notes"
			class="rounded-full bg-conflict px-4 py-1.5 text-sm font-medium whitespace-nowrap text-white shadow-sm transition hover:brightness-110"
		>
			{conflictCount} things don't add up →
		</a>
	</nav>
</header>

<main class="mx-auto max-w-7xl px-4 py-8">
	{@render children()}
</main>

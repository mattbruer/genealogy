<script>
	import { notes } from '#lib/photos.js';
	import NoteCard from '#lib/NoteCard.svelte';

	const sections = [
		{
			kind: 'conflict',
			title: "Things that don't add up",
			intro: 'Places where captions disagree with each other, or with outside records.'
		},
		{
			kind: 'pattern',
			title: 'Patterns & research',
			intro: 'Threads that run across many photos, checked against outside sources where possible.'
		}
	];
</script>

<svelte:head><title>Notes &amp; conflicts · Bruer Family</title></svelte:head>

<div class="mx-auto max-w-3xl space-y-12">
	<p class="text-ink/70">
		Reading all the captions together turns up patterns no single photo shows, and a few
		contradictions worth a second look. Each note also appears under the photos it mentions.
	</p>
	{#each sections as section (section.kind)}
		<section>
			<h2 class="font-serif text-3xl">{section.title}</h2>
			<p class="mt-1 mb-6 text-ink/60">{section.intro}</p>
			<div class="space-y-4">
				{#each notes.filter((n) => n.kind === section.kind) as note (note.title)}
					<NoteCard {note} />
				{/each}
			</div>
		</section>
	{/each}
</div>

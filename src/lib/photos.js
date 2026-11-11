import photoList from './data/photos.json';
import captions from './data/captions.json';
import tags from './data/tags.json';
import observations from './data/observations.json';

/**
 * @typedef {{ id: string, width: number, height: number, enhanced: boolean, caption: string,
 *   year: number | null, yearIsGuess: boolean, families: string[], topics: string[] }} Photo
 * @typedef {{ kind: 'conflict' | 'pattern', title: string, body: string, photos: string[], sources?: string[] }} Observation
 * @typedef {{ query?: string, family?: string, topic?: string, order?: 'oldest' | 'newest' }} Filters
 */

const UNDATED = 9999;

/** Every photo, oldest first; undated photos last. @type {Photo[]} */
export const photos = photoList
	.map((p) => ({ ...p, caption: captions[p.id] ?? '', ...tags[p.id] }))
	.sort((a, b) => (a.year ?? UNDATED) - (b.year ?? UNDATED));

/** @type {Observation[]} */
export const notes = /** @type {Observation[]} */ (observations);

const byId = new Map(photos.map((p) => [p.id, p]));

/** @param {string} id */
export const getPhoto = (id) => byId.get(id);

/** @param {string} id */
export const notesFor = (id) => notes.filter((n) => n.photos.includes(id));

/** @param {string} id @param {'original' | 'enhanced' | 'thumb'} version */
export const imageUrl = (id, version) => `/photos/${id}/${version}.webp`;

/** @param {Photo} p */
export const yearLabel = (p) => (p.year ? `${p.yearIsGuess ? 'c. ' : ''}${p.year}` : '');

/** @param {Photo} p */
export const decadeLabel = (p) => (p.year ? `${Math.floor(p.year / 10) * 10}s` : 'Date unknown');

/** @param {'families' | 'topics'} key */
function countTags(key) {
	const counts = new Map();
	for (const p of photos) for (const t of p[key]) counts.set(t, (counts.get(t) ?? 0) + 1);
	return [...counts].map(([name, count]) => ({ name, count }));
}

export const families = countTags('families');
export const topics = countTags('topics').sort((a, b) => b.count - a.count);

/** @param {Filters} filters */
export function filterPhotos({ query = '', family = '', topic = '', order = 'oldest' }) {
	const words = query.toLowerCase().split(/\s+/).filter(Boolean);
	const result = photos.filter(
		(p) =>
			(!family || p.families.includes(family)) &&
			(!topic || p.topics.includes(topic)) &&
			words.every((w) => p.caption.toLowerCase().includes(w))
	);
	return order === 'newest' ? newestFirst(result) : result;
}

/** @param {Photo[]} list */
function newestFirst(list) {
	const dated = list.filter((p) => p.year).reverse();
	return [...dated, ...list.filter((p) => !p.year)];
}

/** Split a list into runs of the same decade, keeping order. @param {Photo[]} list */
export function groupByDecade(list) {
	/** @type {{ label: string, photos: Photo[] }[]} */
	const groups = [];
	for (const p of list) {
		const label = decadeLabel(p);
		if (groups.at(-1)?.label !== label) groups.push({ label, photos: [] });
		groups.at(-1)?.photos.push(p);
	}
	return groups;
}

import photoList from './data/photos.json';
import captions from './data/captions.json';
import observations from './data/observations.json';

/** @typedef {{ id: string, width: number, height: number, enhanced: boolean, caption: string }} Photo */
/** @typedef {{ kind: 'conflict' | 'pattern', title: string, body: string, photos: string[], sources?: string[] }} Observation */

/** @type {Photo[]} */
export const photos = photoList.map((p) => ({ ...p, caption: captions[p.id] ?? '' }));

/** @type {Observation[]} */
export const notes = /** @type {Observation[]} */ (observations);

const byId = new Map(photos.map((p) => [p.id, p]));

/** @param {string} id */
export const getPhoto = (id) => byId.get(id);

/** @param {string} id */
export const notesFor = (id) => notes.filter((n) => n.photos.includes(id));

/** @param {string} id @param {'original' | 'enhanced' | 'thumb'} version */
export const imageUrl = (id, version) => `/photos/${id}/${version}.webp`;

/** @param {string} query */
export function search(query) {
	const words = query.toLowerCase().split(/\s+/).filter(Boolean);
	if (!words.length) return photos;
	return photos.filter((p) => words.every((w) => p.caption.toLowerCase().includes(w)));
}

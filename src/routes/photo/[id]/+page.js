import { error } from '@sveltejs/kit';
import { photos, getPhoto } from '#lib/photos.js';

export const entries = () => photos.map((p) => ({ id: p.id }));

/** @type {import('./$types').PageLoad} */
export function load({ params }) {
	const photo = getPhoto(params.id);
	if (!photo) error(404, 'Photo not found');
	const i = photos.indexOf(photo);
	return { photo, prev: photos[i - 1]?.id, next: photos[i + 1]?.id };
}

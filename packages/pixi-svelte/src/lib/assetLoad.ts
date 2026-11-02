import * as SPINE_PIXI from '@esotericsoftware/spine-pixi-v8';
import * as PIXI from 'pixi.js';
import type { RawType, RawAsset, RawSpine, RawSprites, SpineSrc, RawAudio } from './types';

const PROCESS_METHOD_MAP = {
	spine: ({ key, rawAsset, src }: { key: string; rawAsset: RawSpine; src: SpineSrc }) => {
		const atlasAsset = rawAsset[src.atlas] as SPINE_PIXI.TextureAtlas;
		const skeletonAsset = rawAsset[src.skeleton] as Uint8Array;
		const attachmentLoader = new SPINE_PIXI.AtlasAttachmentLoader(atlasAsset);
		const parser =
			skeletonAsset instanceof Uint8Array
				? new SPINE_PIXI.SkeletonBinary(attachmentLoader)
				: new SPINE_PIXI.SkeletonJson(attachmentLoader);
		const scale = src?.scale ?? 1;
		parser.scale = scale;
		const skeletonData = parser.readSkeletonData(skeletonAsset);

		return { [key]: skeletonData };
	},
	sprite: ({ key, rawAsset }: { key: string; rawAsset: RawSprites }) => ({ [key]: rawAsset }),
	sprites: ({ rawAsset }: { rawAsset: RawSprites }) => rawAsset.textures,
	// A multi-pack sheet (meta.related_multi_packs) loads as one Spritesheet with the other
	// packs in linkedSheets: the animation is every pack's frames, in frame-name order (the
	// names are zero-padded), so a long or high-res animation can span several textures.
	spriteSheet: ({ key, rawAsset }: { key: string; rawAsset: RawSprites }) => {
		const sheets = [rawAsset, ...((rawAsset as { linkedSheets?: RawSprites[] }).linkedSheets ?? [])];
		if (sheets.length === 1) return { [key]: Object.values(rawAsset.textures) };
		const all = Object.assign({}, ...sheets.map((sheet) => sheet.textures));
		return { [key]: Object.keys(all).sort().map((name) => all[name]) };
	},
	audio: ({ key, rawAsset }: { key: string; rawAsset: RawAudio }) => {
		return { [key]: rawAsset };
	},
} as const;

/** A sheet's Basis twin (<name>.basis.json) first, the plain sheet if it fails. Basis sheets
 *  are encoded premultiplied (bs-render basis_pack.py), and a compressed upload can't
 *  premultiply, so their sources are marked so. */
/** a promise that rejects after `ms` - no single asset may ever hang the loading screen */
export const withTimeout = <T>(promise: Promise<T>, ms: number, what: string) =>
	Promise.race([
		promise,
		new Promise<never>((_, reject) => setTimeout(() => reject(new Error(`timed out after ${ms} ms: ${what}`)), ms)),
	]);

export const loadBasisTwin = async (src: string, onProgress?: (value: number) => void) => {
	try {
		const sheet = await withTimeout(
			PIXI.Assets.load<PIXI.Spritesheet>(src.replace(/\.json$/, '.basis.json'), onProgress),
			4000,
			'basis ' + src,
		);
		for (const s of [sheet, ...(sheet.linkedSheets ?? [])]) {
			s.textureSource.alphaMode = 'premultiplied-alpha';
		}
		return sheet as unknown as RawAsset;
	} catch (error) {
		console.warn('basis sheet failed, using the plain one', src, error);
		return PIXI.Assets.load<RawAsset>(src, onProgress);
	}
};

export const getProcessed = ({
	key,
	type,
	rawAsset,
	src,
}: {
	key: string;
	type: RawType;
	rawAsset: RawAsset;
	src: string | SpineSrc;
}) => {
	if (type === 'font') return; // No need to process raw font data and add it to the loaded assets.
	const processMethod = PROCESS_METHOD_MAP[type];
	if (!processMethod)
		throw Error('No asset process method found, please check the type of the asset.');
	// @ts-expect-error
	return processMethod({ key, rawAsset, src });
};

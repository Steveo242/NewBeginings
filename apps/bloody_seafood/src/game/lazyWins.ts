import * as PIXI from 'pixi.js';
import { withTimeout } from 'pixi-svelte';

import { stateApp } from './stateApp';
import assets from './assets';
import type { BookEvent } from './typesBookEvent';
import { SYMBOL_INFO_MAP } from './constants';

/** every pack's frames in frame-name order (as pixi-svelte's spriteSheet processor) */
const framesOf = (sheet: PIXI.Spritesheet) => {
	const all: Record<string, PIXI.Texture> = Object.assign(
		{},
		...[sheet, ...(sheet.linkedSheets ?? [])].map((s) => s.textures),
	);
	return Object.keys(all)
		.sort()
		.map((name) => all[name]);
};

// The 512px win sheets are too big to keep every symbol's resident on a phone (~40 MB of
// GPU memory each), so they load per round: as soon as the bet's book is in - before the
// reels even start - every symbol the book will win with is fetched and decoded, and the
// rest are released. The lows win most often, so their sheets stay warm. They stay WebP:
// a Basis (UASTC) twin is ~2.3x the download, and with only a handful resident at a time
// the memory it would save matters far less than for the always-resident land/idle sheets.
const WARM = ['L1_win', 'L2_win', 'L3_win'];
export const LAZY_WIN_KEYS = ['H1_win', 'H2_win', 'H3_win', 'H4_win', 'L1_win', 'L2_win', 'L3_win', 'W_win', 'S_win'];

const loading = new Map<string, Promise<void>>();
// v5.5: a sheet is only ever destroyed when nothing can still draw it. Releasing used to
// unload (destroy every texture) the moment a new round's book came in; a symbol whose
// AnimatedSprite still held those textures for a frame or two then drew a texture with no
// source - "Cannot read properties of null (reading '_resourceId')" - and the throw in the
// render loop blanked the board. Now: a sheet must go unused for KEEP_ROUNDS rounds, it is
// first dropped from loadedAssets (so Svelte swaps every SpriteSheet off it), and it is only
// unloaded after a couple of frames when a scan of the stage finds no sprite still bound
// to it. A load that arrives while an unload is in flight waits for it first.
const KEEP_ROUNDS = 2;
const lastNeeded = new Map<string, number>();
const unloading = new Map<string, Promise<void>>();
let round = 0;

const load = async (key: string) => {
	await unloading.get(key);
	if (stateApp.loadedAssets?.[key]) return;
	if (!loading.has(key)) {
		const { src } = assets[key as keyof typeof assets] as { src: string };
		loading.set(
			key,
			withTimeout(PIXI.Assets.load<PIXI.Spritesheet>(src), 20000, key)
				.then((sheet) => {
					stateApp.loadedAssets = { ...stateApp.loadedAssets, [key]: framesOf(sheet) };
				})
				.catch((error) => console.error('win sheet', key, error))
				.finally(() => loading.delete(key)),
		);
	}
	return loading.get(key)!;
};

const frame = () => new Promise<void>((resolve) => requestAnimationFrame(() => resolve()));

type Node = PIXI.Container & Record<string, unknown>;
/** every texture a renderable can hand the batcher: sprites (and animated frames), tiling /
 *  nine-slice sprites, meshes, Graphics texture fills and strokes, particles */
const texturesOf = (node: Node): PIXI.Texture[] => {
	const out: PIXI.Texture[] = [];
	const add = (t: unknown) => t instanceof PIXI.Texture && out.push(t);
	if (node instanceof PIXI.AnimatedSprite) node.textures.forEach(add);
	if ('texture' in node && !(node instanceof PIXI.AbstractText)) add(node.texture);
	if (node instanceof PIXI.Graphics)
		for (const inst of node.context.instructions as { data?: { style?: { texture?: unknown }; image?: unknown } }[]) {
			add(inst.data?.style?.texture);
			add(inst.data?.image);
		}
	if (node instanceof PIXI.ParticleContainer) for (const p of node.particleChildren) add(p.texture);
	return out;
};
/** texture sources / styles a node's filters bind */
const filterResources = (node: PIXI.Container) => {
	const out: unknown[] = [];
	for (const filter of (node.filters ?? []) as PIXI.Filter[]) {
		for (const res of Object.values(filter.resources ?? {})) out.push(res);
	}
	return out;
};
const walk = (visit: (node: Node) => boolean | void) => {
	const stage = stateApp.pixiApplication?.stage;
	if (!stage) return;
	const stack: PIXI.Container[] = [stage];
	while (stack.length) {
		const node = stack.pop()!;
		if (visit(node as Node) === true) return;
		stack.push(...node.children);
	}
};

/** any renderable on the stage still drawing one of these textures */
const boundTo = (textures: Set<PIXI.Texture>) => {
	const sources = new Set([...textures].map((t) => t.source));
	let bound = false;
	walk((node) => {
		bound =
			texturesOf(node).some((t) => textures.has(t) || sources.has(t.source)) ||
			filterResources(node).some((r) => sources.has(r as PIXI.TextureSource) || textures.has(r as PIXI.Texture));
		return bound;
	});
	return bound;
};

// THE v5.5 "render recovered (0 sprite(s))" culprit: Pixi caches each render group's batches
// between frames and only rebuilds them when the structure changes. A sprite that swaps to a
// texture whose source is already in its batch is patched in place (checkAndUpdateTexture),
// so its OLD source stays in that batch's texture list. Once the win sheet was unloaded, the
// cached batch still bound that destroyed source; its style is null and drawing it threw
// "reading '_resourceId'" (Chrome; "addressModeU" in Firefox) - with no sprite left on it.
// So before any unload, every render group is made to rebatch from what is really drawn.
const rebatch = () => {
	const group = stateApp.pixiApplication?.stage?.renderGroup;
	const mark = (g: PIXI.RenderGroup) => {
		g.structureDidChange = true;
		g.renderGroupChildren.forEach(mark);
	};
	if (group) mark(group);
};

const release = (key: string) => {
	const frames = stateApp.loadedAssets?.[key] as PIXI.Texture[] | undefined;
	if (!frames || loading.has(key) || unloading.has(key)) return;
	const { src } = assets[key as keyof typeof assets] as { src: string };
	const textures = new Set(frames);
	const { [key]: _, ...rest } = stateApp.loadedAssets;
	stateApp.loadedAssets = rest; // every SpriteSheet on this key now swaps to no frames
	const job = (async () => {
		// let Svelte apply that and a few frames render without it; never unload while bound
		for (let tries = 0; tries < 20; tries++) {
			await frame();
			await frame();
			if (!boundTo(textures)) {
				// flush the cached batches that may still list the sheet, then unload
				rebatch();
				await frame();
				await frame();
				if (boundTo(textures)) continue;
				rebatch();
				await PIXI.Assets.unload(src).catch(() => {});
				return;
			}
			await new Promise((r) => setTimeout(r, 500));
		}
		// still bound after ~10 s: keep it (a leak beats a crash) and put it back
		stateApp.loadedAssets = { ...stateApp.loadedAssets, [key]: frames };
	})().finally(() => unloading.delete(key));
	unloading.set(key, job);
};

/** Win sheet keys a bet's book will play (cluster wins + the scatter/wild that land in them). */
export const winKeysOf = (bookEvents: BookEvent[]) => {
	const keys = new Set<string>();
	for (const event of bookEvents) {
		if (event.type !== 'winInfo') continue;
		for (const win of event.wins) keys.add(`${win.symbol}_win`);
	}
	if (bookEvents.some((event) => event.type === 'freeSpinTrigger')) keys.add('S_win');
	return [...keys].filter((key) => LAZY_WIN_KEYS.includes(key));
};

/** Start loading this round's win sheets (don't await: decoding runs while the reels spin)
 *  and release the ones it won't use. */
export const prepareWins = (bookEvents: BookEvent[]) => {
	installRenderGuard();
	round += 1;
	const need = winKeysOf(bookEvents);
	for (const key of need) lastNeeded.set(key, round);
	for (const key of LAZY_WIN_KEYS) {
		if (need.includes(key) || WARM.includes(key)) continue;
		if (round - (lastNeeded.get(key) ?? 0) > KEEP_ROUNDS) release(key);
	}
	return Promise.all([...new Set([...need, ...WARM])].map(load));
};

// The render loop's last line of defence: if anything ever draws a texture whose source is
// gone, the throw would stop every later frame (a blank board). Catch it, walk EVERY
// renderable and filter: an animated symbol goes to its STATIC texture (always resident) at
// the static's size - a reviewer never sees a missing symbol -, anything else to the empty
// texture, a dead filter is dropped. Then every render group rebatches (which also clears
// a cached batch that still lists a dead source - see rebatch). Logged to the console with
// each offender's class/label/parent chain; on screen only with ?diag=1.
type Info = { assetKey: string; sizeRatios: { width: number; height: number } };
const dead = (t: PIXI.Texture | undefined) => !t || t.destroyed || !t.source || t.source.destroyed || !t.source.style;
const deadResource = (r: unknown) =>
	r === null ||
	(r instanceof PIXI.TextureSource && (r.destroyed || !r.style)) ||
	(r instanceof PIXI.TextureStyle && r.destroyed) ||
	(r instanceof PIXI.Texture && dead(r));
const toStatic = (node: PIXI.AnimatedSprite) => {
	// SymbolAnimatedSprite labels its sprite with the sheet key: <SYMBOL>_<state>
	const [symbol, state] = String(node.label ?? '').split('_');
	const info = (SYMBOL_INFO_MAP as unknown as Record<string, Record<string, Info>>)[symbol];
	const stat = info?.static;
	const tex = stat && (stateApp.loadedAssets?.[stat.assetKey] as PIXI.Texture | undefined);
	const from = info?.[state];
	if (!tex || dead(tex) || !from) return false;
	const w = node.width * (stat.sizeRatios.width / from.sizeRatios.width);
	const h = node.height * (stat.sizeRatios.height / from.sizeRatios.height);
	node.stop();
	node.textures = [tex];
	node.width = w;
	node.height = h;
	return true;
};
// class names survive minification only this way
const KINDS: [string, abstract new (...a: never[]) => unknown][] = [
	['AnimatedSprite', PIXI.AnimatedSprite],
	['TilingSprite', PIXI.TilingSprite],
	['NineSliceSprite', PIXI.NineSliceSprite],
	['Sprite', PIXI.Sprite],
	['Mesh', PIXI.Mesh],
	['Graphics', PIXI.Graphics],
	['BitmapText', PIXI.BitmapText],
	['Text', PIXI.AbstractText],
	['ParticleContainer', PIXI.ParticleContainer],
];
const describe = (node: PIXI.Container) => {
	const kind = KINDS.find(([, k]) => node instanceof k)?.[0] ?? 'Container';
	const chain: string[] = [];
	for (let p = node.parent; p && chain.length < 6; p = p.parent) chain.push(p.label || '?');
	return `${kind} "${node.label || ''}" < ${chain.join(' < ')}`;
};
let guarded = false;
const reported = new Set<string>();
const sanitize = () => {
	const found: string[] = [];
	walk((node) => {
		const filters = (node.filters ?? []) as PIXI.Filter[];
		const live = filters.filter((f) => f.resources && !Object.values(f.resources ?? {}).some(deadResource));
		if (live.length !== filters.length) {
			node.filters = live;
			found.push('filter on ' + describe(node));
		}
		if (!texturesOf(node).some(dead)) return;
		found.push(describe(node));
		if (node instanceof PIXI.AnimatedSprite) {
			if (!toStatic(node)) {
				node.stop();
				node.textures = [PIXI.Texture.EMPTY];
			}
		} else if (node instanceof PIXI.Sprite || node instanceof PIXI.TilingSprite || node instanceof PIXI.NineSliceSprite || node instanceof PIXI.Mesh) {
			node.texture = PIXI.Texture.EMPTY;
		} else if (node instanceof PIXI.ParticleContainer) {
			for (const p of node.particleChildren) if (dead(p.texture)) p.texture = PIXI.Texture.EMPTY;
		} else if (node instanceof PIXI.Graphics) {
			node.visible = false;
		}
	});
	rebatch();
	return found;
};
const verbose = typeof location !== 'undefined' && new URLSearchParams(location.search).get('diag') === '1';
export const installRenderGuard = () => {
	const app = stateApp.pixiApplication;
	if (guarded || !app?.renderer) return;
	guarded = true;
	// ?diag=1: a handle for forcing teardown sequences from the console / a test harness
	if (verbose && typeof window !== 'undefined') (window as unknown as Record<string, unknown>).__bsDiag = { app, rebatch, sanitize };
	const render = app.renderer.render.bind(app.renderer) as (...a: unknown[]) => void;
	(app.renderer as unknown as { render: (...a: unknown[]) => void }).render = (...args: unknown[]) => {
		try {
			render(...args);
		} catch (error) {
			const found = sanitize();
			const msg =
				`render recovered (${found.length ? found.join('; ') : 'stale cached batch only'}): ` +
				(error instanceof Error ? error.message : String(error));
			if (reported.has(msg)) return;
			reported.add(msg);
			console.warn(msg);
			if (verbose && typeof window !== 'undefined') window.dispatchEvent(new ErrorEvent('error', { message: msg }));
		}
	};
};

/** the current round's prepareWins(); the win handlers await it (normally long settled) */
export const winsReady: { promise: Promise<unknown> } = { promise: Promise.resolve() };

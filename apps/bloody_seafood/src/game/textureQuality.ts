import { Filter, loadTextures, type Application, type ResolvedAsset } from 'pixi.js';

// Symbols are rendered at ~176-560px and drawn at ~55-100px (about a third of that on a
// phone). Without mipmaps the GPU minifies with a 2x2 bilinear tap, which skips most
// source pixels: the art looked grainy and sparkled as it moved. Mipmaps let every
// texture shrink cleanly. Set before any asset loads (imported first by +layout.svelte).
//
// Only for loaded image files. Not TextureSource.defaultOptions: that also gives mip
// levels to the render targets filters draw into (the fall blur), and WebGPU cannot
// render into those - the canvas stayed black while the audio played.
const load = loadTextures.load!;
loadTextures.load = function (url: string, asset: ResolvedAsset, loader) {
	const data = { autoGenerateMipmaps: true, scaleMode: 'linear', ...asset?.data };
	return load.call(this, url, { ...asset, data }, loader);
};

// Filters render into their own texture at Filter.defaultOptions.resolution, which is 1 -
// while the app renders at devicePixelRatio. The colour grade on the symbol layer
// (vividFilter) therefore drew every symbol at half resolution on a 2x screen (a third
// on 3x phones) and stretched it back up: the whole board read soft. 'inherit' renders
// each filter at its target's resolution.
Filter.defaultOptions.resolution = 'inherit';

// The full-screen background filters (sky / sea displacement, the grade, the lightning
// flash, the tank caustics) stay at resolution 1 for speed on 2-3x phones. But a filter
// must never render ABOVE the screen's resolution: Pixi v8 then clips its output to
// (screen resolution / filter resolution) of the screen - at a zoomed-out desktop browser
// (devicePixelRatio 0.9 at 90%) the sky and sea stopped 90% of the way across, the dock
// and ship running on past them. Capped at the renderer's resolution, every tick.
export const fxResolution = (app: Application | undefined) => Math.min(1, app?.renderer?.resolution ?? 1);

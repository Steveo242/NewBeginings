import { Filter, loadTextures, type ResolvedAsset } from 'pixi.js';

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

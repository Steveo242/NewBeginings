import { GPU, LOW_MEMORY } from './device';

// Renderer options for the low-memory (phone) path, read by pixi-svelte's
// InitialiseApplication: WebGL (WebGPU on Android is new and the v5 phones failed to load),
// no MSAA (a 4x multisampled 3x-density screen alone is tens of MB) and at most 2x density.
if (LOW_MEMORY) {
	(globalThis as { __PIXI_INIT?: object }).__PIXI_INIT = {
		preference: 'webgl',
		antialias: false,
		resolution: Math.min(2, typeof devicePixelRatio === 'number' ? devicePixelRatio : 1),
	};
}
(globalThis as { __BS_DEVICE?: object }).__BS_DEVICE = { lowMemory: LOW_MEMORY, ...GPU };

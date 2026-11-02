// Which art set this device gets. Phones (and anything short of graphics memory) take the
// half-resolution mirror (static/assets/sprites_m, tools/make_mobile_sprites.py): a
// quarter of the GPU memory, no texture over 2048 px. v5 kept ~340 MB of textures
// resident and some Android phones lost the WebGL context on load. ?lowmem=1 / ?lowmem=0
// force either set (testing).

/** the GPU's texture size limit, from a throwaway WebGL context (released at once) */
const probe = () => {
	if (typeof document === 'undefined') return { maxTexture: 4096, renderer: 'n/a' };
	try {
		const canvas = document.createElement('canvas');
		const gl = (canvas.getContext('webgl2') || canvas.getContext('webgl')) as WebGLRenderingContext | null;
		if (!gl) return { maxTexture: 0, renderer: 'no WebGL' };
		const info = gl.getExtension('WEBGL_debug_renderer_info');
		const renderer = String(info ? gl.getParameter(info.UNMASKED_RENDERER_WEBGL) : gl.getParameter(gl.RENDERER));
		const maxTexture = Number(gl.getParameter(gl.MAX_TEXTURE_SIZE));
		gl.getExtension('WEBGL_lose_context')?.loseContext();
		return { maxTexture, renderer };
	} catch {
		return { maxTexture: 0, renderer: 'probe failed' };
	}
};

export const GPU = probe();

const forced = typeof location !== 'undefined' ? new URLSearchParams(location.search).get('lowmem') : null;
const coarse = typeof matchMedia !== 'undefined' && matchMedia('(pointer: coarse)').matches;
const smallScreen = typeof screen !== 'undefined' && Math.min(screen.width, screen.height) < 900;
const memory = typeof navigator !== 'undefined' ? ((navigator as { deviceMemory?: number }).deviceMemory ?? 8) : 8;

/** the low-memory (phone) path: half-res art, no mipmaps, wins loaded only for winners */
export const LOW_MEMORY =
	forced === '1' || (forced !== '0' && ((coarse && smallScreen) || memory <= 4 || GPU.maxTexture < 4096));

/** a loose image URL or a sheet JSON URL, swapped to its half-resolution twin */
export const lowMemoryUrl = (href: string, type: string) => {
	if (!href.includes('/assets/sprites/')) return href;
	const url = href.replace('/assets/sprites/', '/assets/sprites_m/');
	// loose images carry Pixi's resolution suffix, so they keep their logical size
	return type === 'sprite' ? url.replace(/(\.(png|webp|jpe?g))$/i, '@0.5x$1') : url;
};

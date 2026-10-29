import * as PIXI from 'pixi.js';

// Small procedural textures for symbol FX, drawn once on first use.

const canvasTexture = (w: number, h: number, draw: (ctx: CanvasRenderingContext2D) => void) => {
	const canvas = document.createElement('canvas');
	canvas.width = w;
	canvas.height = h;
	draw(canvas.getContext('2d')!);
	return PIXI.Texture.from(canvas);
};

let band: PIXI.Texture | undefined;
/** A soft vertical light bar, bright in the middle and gone at both edges: the specular sweep. */
export const shineBandTexture = () =>
	(band ??= canvasTexture(64, 4, (ctx) => {
		const g = ctx.createLinearGradient(0, 0, 64, 0);
		g.addColorStop(0, 'rgba(255,255,255,0)');
		g.addColorStop(0.35, 'rgba(255,250,235,0.35)');
		g.addColorStop(0.5, 'rgba(255,255,255,1)');
		g.addColorStop(0.65, 'rgba(255,250,235,0.35)');
		g.addColorStop(1, 'rgba(255,255,255,0)');
		ctx.fillStyle = g;
		ctx.fillRect(0, 0, 64, 4);
	}));

let star: PIXI.Texture | undefined;
/** A four-point glint: a hot core with long thin rays, for sparkles on polished metal. */
export const sparkleTexture = () =>
	(star ??= canvasTexture(64, 64, (ctx) => {
		const c = 32;
		const core = ctx.createRadialGradient(c, c, 0, c, c, 14);
		core.addColorStop(0, 'rgba(255,255,255,1)');
		core.addColorStop(0.3, 'rgba(255,245,210,0.6)');
		core.addColorStop(1, 'rgba(255,230,160,0)');
		ctx.fillStyle = core;
		ctx.fillRect(0, 0, 64, 64);
		for (const [dx, dy] of [
			[1, 0],
			[0, 1],
		]) {
			const g = ctx.createLinearGradient(c - 32 * dx, c - 32 * dy, c + 32 * dx, c + 32 * dy);
			g.addColorStop(0, 'rgba(255,255,255,0)');
			g.addColorStop(0.5, 'rgba(255,255,255,1)');
			g.addColorStop(1, 'rgba(255,255,255,0)');
			ctx.fillStyle = g;
			if (dx) ctx.fillRect(0, c - 1.5, 64, 3);
			else ctx.fillRect(c - 1.5, 0, 3, 64);
		}
	}));

let vivid: PIXI.ColorMatrixFilter | undefined;
/**
 * The board's colour grade: richer colour, a touch more contrast and light, so the fish
 * and chum read saturated and bright against the dark tank rather than photo-flat.
 * One shared filter on the symbol layer, not one per symbol.
 */
export const vividFilter = () => {
	if (vivid) return vivid;
	vivid = new PIXI.ColorMatrixFilter();
	vivid.saturate(0.5, false);
	vivid.contrast(0.2, true);
	vivid.brightness(1.1, true);
	return vivid;
};

let drop: PIXI.Texture | undefined;
/** A glossy blood droplet, round end down, anchored (0.5, 0.25) at its neck: the falling drip. */
export const bloodDropTexture = () =>
	(drop ??= canvasTexture(48, 72, (ctx) => {
		ctx.beginPath();
		ctx.moveTo(24, 2);
		ctx.bezierCurveTo(30, 22, 44, 36, 44, 50);
		ctx.arc(24, 50, 20, 0, Math.PI, false);
		ctx.bezierCurveTo(4, 36, 18, 22, 24, 2);
		const body = ctx.createRadialGradient(18, 46, 2, 24, 50, 26);
		body.addColorStop(0, '#d8222b');
		body.addColorStop(0.6, '#8e0a12');
		body.addColorStop(1, '#4a0307');
		ctx.fillStyle = body;
		ctx.fill();
		ctx.beginPath();
		ctx.ellipse(17, 44, 4, 7, -0.4, 0, Math.PI * 2);
		ctx.fillStyle = 'rgba(255,235,230,0.85)';
		ctx.fill();
	}));

const solids = new Map<number, PIXI.ColorMatrixFilter>();
/** Paints whatever it filters one flat colour, keeping its alpha: a silhouette for outlines. */
export const solidFilter = (color: number) => {
	let f = solids.get(color);
	if (!f) {
		f = new PIXI.ColorMatrixFilter();
		const r = ((color >> 16) & 255) / 255;
		const g = ((color >> 8) & 255) / 255;
		const b = (color & 255) / 255;
		f.matrix = [0, 0, 0, 0, r, 0, 0, 0, 0, g, 0, 0, 0, 0, b, 0, 0, 0, 1, 0];
		solids.set(color, f);
	}
	return f;
};

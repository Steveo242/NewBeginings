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

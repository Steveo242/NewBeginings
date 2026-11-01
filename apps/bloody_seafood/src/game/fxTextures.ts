import * as PIXI from 'pixi.js';

// Small procedural textures for symbol FX, drawn once on first use.

const canvasTexture = (w: number, h: number, draw: (ctx: CanvasRenderingContext2D) => void) => {
	const canvas = document.createElement('canvas');
	canvas.width = w;
	canvas.height = h;
	draw(canvas.getContext('2d')!);
	return PIXI.Texture.from(canvas);
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
		f = new PIXI.ColorMatrixFilter({ resolution: 'inherit' });
		const r = ((color >> 16) & 255) / 255;
		const g = ((color >> 8) & 255) / 255;
		const b = (color & 255) / 255;
		f.matrix = [0, 0, 0, 0, r, 0, 0, 0, 0, g, 0, 0, 0, 0, b, 0, 0, 0, 1, 0];
		solids.set(color, f);
	}
	return f;
};

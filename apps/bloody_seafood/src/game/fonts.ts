import { FillGradient } from 'pixi.js';

// The game's one display face: TeX Gyre Bonum Bold (GUST Font License,
// static/assets/fonts/bs_display.LICENSE.txt), the same face the WILD banner
// lettering was modelled from. Latin subset, 18 KB.
export const DISPLAY_FONT_FAMILY = 'BloodySeafoodDisplay';
export const DISPLAY_FONT = `${DISPLAY_FONT_FAMILY}, Georgia, serif`;

const DISPLAY_FONT_URL = new URL('../../assets/fonts/bs_display.woff2', import.meta.url).href;

let loading: Promise<void> | undefined;

// Pixi rasterises a Text once, when it is created, so the face must be ready
// before the first label is drawn. Started from +layout, behind the publisher
// intro; a failure just leaves the Georgia fallback in place.
export const loadDisplayFont = () => {
	loading ??= (async () => {
		try {
			const face = new FontFace(DISPLAY_FONT_FAMILY, `url(${DISPLAY_FONT_URL})`, { weight: '700' });
			document.fonts.add(await face.load());
		} catch (error) {
			console.warn('display font failed to load', error);
		}
	})();
	return loading;
};

// Polished brass, lit from above to match the tank's key light: pale highlight
// at the cap height, warm gold through the body, dark bronze at the baseline.
export const brassFill = () =>
	new FillGradient({
		type: 'linear',
		start: { x: 0, y: 0 },
		end: { x: 0, y: 1 },
		textureSpace: 'local',
		colorStops: [
			{ offset: 0, color: 0xfff4c8 },
			{ offset: 0.38, color: 0xffd35a },
			{ offset: 0.62, color: 0xd99a22 },
			{ offset: 1, color: 0x7a4a0e },
		],
	});

// Every piece of in-game display text shares this look: brass face, a thick
// oxblood-to-black outline so it reads over any symbol, and a soft drop shadow.
export const displayTextStyle = (fontSize: number) => ({
	fontFamily: DISPLAY_FONT,
	fontSize,
	fontWeight: 'bold' as const,
	align: 'center' as const,
	fill: brassFill(),
	stroke: { color: 0x2a0006, width: Math.max(3, fontSize * 0.09), join: 'round' as const },
	dropShadow: { color: 0x000000, alpha: 0.7, blur: fontSize * 0.06, distance: fontSize * 0.05, angle: Math.PI / 2 },
	letterSpacing: fontSize * 0.02,
});

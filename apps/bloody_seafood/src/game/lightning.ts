// Win highlights are drawn as electricity: every colour here is a lightning colour - a
// saturated glow round a near-white core - never a flat paint colour.

export type Bolt = { glow: number; mid: number };

/** each symbol's own lightning, for the outline traced round its silhouette */
export const SYMBOL_BOLT: Record<string, Bolt> = {
	H1: { glow: 0xff1a3c, mid: 0xff9aa8 }, // blood-red lightning: the shark
	H2: { glow: 0xff1ae0, mid: 0xffa6f4 }, // magenta
	H3: { glow: 0x8a2bff, mid: 0xcfb0ff }, // violet
	H4: { glow: 0x22ff5e, mid: 0xb6ffc8 }, // toxic green
	H5: { glow: 0x22ff5e, mid: 0xb6ffc8 },
	W: { glow: 0xffc400, mid: 0xfff2a8 }, // gold
	S: { glow: 0xff7a00, mid: 0xffcf96 }, // molten orange
	L1: { glow: 0x00e5ff, mid: 0xaaf7ff }, // cyan
	L2: { glow: 0x2a6bff, mid: 0xa8c2ff }, // electric blue
	L3: { glow: 0xd4ff00, mid: 0xf2ffaa }, // sulphur
	L4: { glow: 0x00e5ff, mid: 0xaaf7ff },
};

/** the cell boxes: one lightning for every premium win, another for every low */
export const SQUARE_BOLT = {
	high: { glow: 0xffb000, mid: 0xffe68a } as Bolt, // gold lightning
	low: { glow: 0x1f7bff, mid: 0xa4cbff } as Bolt, // electric blue lightning
};

export const isHighValue = (name: string) => ['H1', 'H2', 'H3', 'H4', 'H5', 'W', 'S'].includes(name);

/** The storm's lightning, live: Background writes the strike's brightness (0..1) here every
 *  frame while the bonus storm is in, and the win highlights surge with it. */
export const storm = { pulse: 0 };

/** A jagged bolt from a to b by midpoint displacement; `rough` is the first offset's size. */
export const boltPoints = (ax: number, ay: number, bx: number, by: number, rough: number) => {
	let pts: [number, number][] = [
		[ax, ay],
		[bx, by],
	];
	for (let d = rough; d > 2; d *= 0.5) {
		const next: [number, number][] = [pts[0]];
		for (let i = 1; i < pts.length; i++) {
			const [x0, y0] = pts[i - 1];
			const [x1, y1] = pts[i];
			const len = Math.hypot(x1 - x0, y1 - y0) || 1;
			const off = (Math.random() - 0.5) * d;
			next.push([(x0 + x1) / 2 + (-(y1 - y0) / len) * off, (y0 + y1) / 2 + ((x1 - x0) / len) * off], [x1, y1]);
		}
		pts = next;
	}
	return pts;
};

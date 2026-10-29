<script lang="ts">
	// Lightning boxes round winning cells: each side a crackling, jagged bolt - wide
	// coloured glow, bright arc, white-hot core - re-struck ~18 times a second so it
	// flickers like real electricity. Gold lightning for every premium win, electric blue
	// for every low (game/lightning.ts). They strike as the symbols win, linger through the
	// burst while the reels refill, and fade once the reels have settled. In the bonus storm
	// every bolt of lightning surges them.
	import * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { getContextParent } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { SYMBOL_SIZE } from '../game/constants';
	import { getSymbolX } from '../game/utils';
	import { SQUARE_BOLT, boltPoints, isHighValue, storm } from '../game/lightning';

	const context = getContext();
	const parent = getContextParent();
	const root = new PIXI.Container();
	parent.addToParent(root);

	const HALF = SYMBOL_SIZE * 0.47;
	const RESTRIKE_MS = 55;
	const FADE_MS = 700;
	/** never hang about longer than this, whatever the round does */
	const MAX_LIFE_MS = 9000;

	type Cell = { x: number; y: number; high: boolean; g: PIXI.Graphics; born: number; fadeAt: number; struck: number };
	const cells = new Map<string, Cell>();

	const add = (reel: number, row: number) => {
		const key = `${reel},${row}`;
		const reelSymbol = context.stateGame.board[reel]?.reelState?.symbols?.[row];
		if (!reelSymbol || (reelSymbol.rawSymbol.name as string) === 'M') return;
		cells.get(key)?.g.destroy();
		const g = new PIXI.Graphics();
		g.blendMode = 'add';
		root.addChild(g);
		cells.set(key, {
			x: getSymbolX(reel),
			y: reelSymbol.symbolY.current,
			high: isHighValue(reelSymbol.rawSymbol.name),
			g,
			born: performance.now(),
			fadeAt: Infinity,
			struck: 0,
		});
	};

	const fadeAll = () => {
		const now = performance.now();
		for (const cell of cells.values()) cell.fadeAt = Math.min(cell.fadeAt, now);
	};

	context.eventEmitter.subscribeOnMount({
		boardWithAnimateSymbols: ({ symbolPositions }) => {
			for (const { reel, row } of symbolPositions) add(reel, row);
		},
		// the reels have refilled and come to rest: the boxes let go
		boardSettle: () => fadeAll(),
	});

	const strike = (cell: Cell, level: number) => {
		const { x, y, g } = cell;
		const rough = SYMBOL_SIZE * (cell.high ? 0.1 : 0.075);
		const corners: [number, number][] = [
			[x - HALF, y - HALF],
			[x + HALF, y - HALF],
			[x + HALF, y + HALF],
			[x - HALF, y + HALF],
		];
		const paths = corners.map((a, i) => {
			const b = corners[(i + 1) % 4];
			return boltPoints(a[0], a[1], b[0], b[1], rough);
		});
		// premium boxes throw the odd arc off a corner
		if (cell.high && Math.random() < 0.35) {
			const [cx, cy] = corners[Math.floor(Math.random() * 4)];
			const dx = Math.sign(cx - x);
			const dy = Math.sign(cy - y);
			const len = SYMBOL_SIZE * (0.2 + Math.random() * 0.25);
			paths.push(boltPoints(cx, cy, cx + dx * len, cy + dy * len * (0.4 + Math.random()), rough * 0.6));
		}
		const bolt = cell.high ? SQUARE_BOLT.high : SQUARE_BOLT.low;
		g.clear();
		const layer = (width: number, color: number, alpha: number) => {
			for (const pts of paths) {
				g.moveTo(pts[0][0], pts[0][1]);
				for (const [px, py] of pts.slice(1)) g.lineTo(px, py);
			}
			g.stroke({ width, color, alpha: Math.min(1, alpha), cap: 'round', join: 'round' });
		};
		layer((cell.high ? 16 : 12) * (0.8 + 0.4 * level), bolt.glow, 0.32 * level);
		layer(cell.high ? 5.5 : 4.5, bolt.glow, 0.9 * level);
		layer(cell.high ? 2.6 : 2, bolt.mid, level);
		layer(1.1, 0xffffff, level);
	};

	const tick = () => {
		const now = performance.now();
		for (const [key, cell] of cells) {
			const age = now - cell.born;
			const fading = Math.max(0, now - cell.fadeAt);
			const life = Math.max(0, 1 - fading / FADE_MS);
			if (life <= 0 || age > MAX_LIFE_MS) {
				cell.g.destroy();
				cells.delete(key);
				continue;
			}
			if (now - cell.struck < RESTRIKE_MS) continue;
			cell.struck = now;
			// the strike, then a live flicker; premiums burn hotter; the storm surges it
			const hit = Math.max(0, 1 - age / 400);
			const flicker = 0.65 + 0.35 * Math.random();
			const level = ((cell.high ? 1 : 0.8) * flicker + hit * 0.8 + storm.pulse * 1.2) * life;
			strike(cell, level);
		}
	};
	context.stateApp.pixiApplication?.ticker.add(tick);

	onDestroy(() => {
		context.stateApp.pixiApplication?.ticker.remove(tick);
		root.destroy({ children: true });
	});
</script>

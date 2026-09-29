<script lang="ts">
	import { Container, Rectangle, Sprite } from 'pixi-svelte';
	import { stateUi } from 'state-shared';
	import { BLACK } from 'constants-shared/colors';
	import type { LayoutUiProps } from 'components-ui-pixi/src/types';
	import { UI_BASE_SIZE } from 'components-ui-pixi/src/constants';

	import { getContext } from '../game/context';
	import { BOARD_SIZES, SYMBOL_SIZE } from '../game/constants';
	import BarButton, { type BarButtonKind } from './bar3d/BarButton.svelte';
	import SpinButton3D from './bar3d/SpinButton3D.svelte';
	import ReplayButton3D from './bar3d/ReplayButton3D.svelte';
	import { isReplay } from '../game/replay';
	import NineSlice from './bar3d/NineSlice.svelte';
	import BarLabel from './bar3d/BarLabel.svelte';
	import LabelPlate from './bar3d/LabelPlate.svelte';

	const props: LayoutUiProps = $props();
	const context = getContext();

	const canvas = $derived(context.stateLayoutDerived.canvasSizes());
	const main = $derived(context.stateLayoutDerived.mainLayout());

	// Everything is authored in the shared controls' own units (UI_BASE_SIZE = one icon
	// button) and each group is scaled by a single factor, so sizes and positions always
	// scale together - scaling them off different axes once made every control overlap
	// its neighbour on portrait.
	//
	// Two arrangements, the way the top studios lay a slot out:
	// - SIDE (desktop, landscape phones): the play controls are a cluster in the open sky
	//   right of the tank - bet -/+, a big spin with autoplay and turbo either side - the
	//   bonus buy is a large plaque in the sky left of it, and balance, win and the menu
	//   icons sit on a slim dark strip along the bottom edge.
	// - BOTTOM (portrait, near-square): one riveted panel under the board.
	// Reviewers marked the old single strip of equal-sized portholes down three times
	// ("poor bet UI bar"): the spin barely outranked the icons and the amounts read as
	// form fields.
	const B = UI_BASE_SIZE;
	const GAP = 46;
	const LABEL_W = 400;
	const LABEL_H = 132;
	const PLATE_H = LABEL_H * 1.12;
	/** Stacked labels draw downwards from their origin, so lift them to sit centred. */
	const LABEL_SHIFT_Y = -LABEL_H * 0.4;
	const MARGIN = 8;

	// ------------------------------------------------------------- board geometry
	// Where the tank actually is on the canvas, from the board's own layout, so the
	// controls stay off it if the board moves. The iron frame reaches past the grid: the
	// side overhang is hud.ts's FRAME_OVERHANG, the base (beam + plinth) was measured
	// off a 1920x1080 capture.
	const FRAME_SIDE = SYMBOL_SIZE * 0.95;
	const FRAME_BELOW = SYMBOL_SIZE * 1.5;
	const board = $derived(context.stateGameDerived.boardLayout());
	const boardCx = $derived(canvas.width * 0.5 + (board.x - main.width * 0.5) * main.scale);
	const boardCy = $derived(canvas.height * 0.5 + (board.y - main.height * 0.5) * main.scale);
	const boardBottom = $derived(boardCy + BOARD_SIZES.height * 0.5 * main.scale);
	const tankRight = $derived(boardCx + (BOARD_SIZES.width * 0.5 + FRAME_SIDE) * main.scale);
	const tankBottom = $derived(boardBottom + FRAME_BELOW * main.scale);

	// ------------------------------------------------------------------ SIDE mode
	const SPIN_BIG = B * 2.1;
	const SIDE_GAP = 30;
	const CLUSTER_W = B + SIDE_GAP + LABEL_W + SIDE_GAP + B;
	const CLUSTER_H = LABEL_H + GAP + SPIN_BIG;
	const SIDE_MARGIN = 16;
	/** the spin never needs to be bigger than this on screen (px): top-studio desktop size */
	const MAX_SIDE_SCALE = 0.46;
	const MIN_SIDE_SCALE = 0.2;
	/** the buy plaque, relative to BarButton's own buy size (1.9 B wide) */
	const BUY_K = 1.5;

	const STRIP_UNITS = B + 30;
	const ICONS = ['rules', 'pay', 'settings', 'sound'] as const;
	const ICON_GAP = 30;
	const ICONS_W = ICONS.length * B + (ICONS.length - 1) * ICON_GAP;
	const STRIP_LABEL_SPACING = LABEL_W + 60;

	const side = $derived.by(() => {
		const roomW = canvas.width - tankRight - SIDE_MARGIN * 2;
		// the strip: as tall as the controls want, but never over the tank's base
		const q0 = Math.min(roomW / CLUSTER_W, (canvas.height * 0.27) / SPIN_BIG, MAX_SIDE_SCALE);
		const stripScale = Math.min(
			q0,
			Math.max(canvas.height - tankBottom - 2, 0) / STRIP_UNITS,
			canvas.width / (ICONS_W * 2 + STRIP_LABEL_SPACING * 2 + 200),
		);
		const stripH = STRIP_UNITS * stripScale;
		const q = Math.min(q0, (canvas.height - stripH - SIDE_MARGIN * 2) / CLUSTER_H);
		const cx = tankRight + SIDE_MARGIN + roomW * 0.5;
		// centred on the board, but never down into the strip
		const cy = Math.min(boardCy, canvas.height - stripH - SIDE_MARGIN - (CLUSTER_H * q) / 2);
		return {
			ok:
				!context.stateLayoutDerived.isStacked() &&
				q >= MIN_SIDE_SCALE &&
				stripScale >= MIN_SIDE_SCALE * 0.8,
			q,
			cx,
			cy,
			// the board is centred, so the room left of the tank mirrors the right
			lx: 2 * boardCx - cx,
			stripScale,
			stripH,
		};
	});

	// ---------------------------------------------------------------- BOTTOM mode
	const SPIN = B * 1.8;

	const SLOT_W: Record<string, number> = {
		menu: B,
		auto: B,
		turbo: B,
		buy: B * 1.9,
		dec: B,
		inc: B,
		spin: SPIN,
		balance: LABEL_W,
		win: LABEL_W,
		bet: LABEL_W,
	};

	const LABEL_KEYS = ['balance', 'win', 'bet'];
	const BUTTON_KEYS: Record<string, BarButtonKind> = {
		menu: 'menu',
		buy: 'buy',
		dec: 'dec',
		inc: 'inc',
		auto: 'auto',
		turbo: 'turbo',
	};
	/** 9-slice corner size, in texture px (build_ui3d.py panel render) */
	const PANEL_BORDER = 80;
	// room round the controls for the panel's rim, and for the 3D buttons, whose art
	// (shadow included) is drawn 1.3x their slot
	const PANEL_PAD = 64;
	const ROW_GAP = 32;

	type Row = { keys: string[]; height: number };

	const arrangements: Row[][] = [
		[
			{ height: LABEL_H, keys: ['balance', 'win', 'bet'] },
			{ height: SPIN, keys: ['menu', 'buy', 'dec', 'spin', 'inc', 'auto', 'turbo'] },
		],
		[
			{ height: LABEL_H, keys: ['balance', 'win'] },
			{ height: SPIN, keys: ['menu', 'auto', 'spin', 'turbo', 'buy'] },
			{ height: B, keys: ['dec', 'bet', 'inc'] },
		],
	];

	// A replay only watches one finished round: no balance, no changing the play amount,
	// no bonus purchase or autoplay. The play slot becomes the replay-again button.
	const REPLAY_HIDDEN = ['balance', 'buy', 'dec', 'inc', 'auto'];
	const shown = (key: string) => !(isReplay() && REPLAY_HIDDEN.includes(key));
	const forMode = (rows: Row[]) =>
		rows
			.map((row) => ({ ...row, keys: row.keys.filter(shown) }))
			.filter((row) => row.keys.length > 0);

	const WIDTH_RATIO = 0.96;
	const MAX_SCALE = 0.42;

	// The band left under the tank is the bar's real height budget - sizing against it
	// rather than a flat fraction of the canvas is what keeps the bar off the reels.
	const roomBelowBoard = $derived(canvas.height - boardBottom - MARGIN);

	const measure = (rows: Row[]) => {
		const laid = rows.map((row) => {
			const width =
				row.keys.reduce((sum, key) => sum + SLOT_W[key], 0) + GAP * (row.keys.length - 1);
			const centers: Record<string, number> = {};
			let cursor = -width * 0.5;
			for (const key of row.keys) {
				centers[key] = cursor + SLOT_W[key] * 0.5;
				cursor += SLOT_W[key] + GAP;
			}
			return { ...row, width, centers };
		});

		const width = Math.max(...laid.map((row) => row.width));
		const height = laid.reduce((sum, row) => sum + row.height, 0) + ROW_GAP * (laid.length - 1);

		let cursor = -height * 0.5;
		const placed = laid.map((row) => {
			const y = cursor + row.height * 0.5;
			cursor += row.height + ROW_GAP;
			return { ...row, y };
		});

		// the panel (rim included) is what has to fit - measuring only the controls let
		// its bottom run off the canvas on desktop
		const scale = Math.min(
			(canvas.width * WIDTH_RATIO) / (width + PANEL_PAD * 2),
			Math.max(roomBelowBoard, 1) / (height + PANEL_PAD * 2),
			MAX_SCALE,
		);

		return { rows: placed, width, height, scale };
	};

	// the single two-row panel while it stays comfortable, else the three-row stack
	const MIN_COMFORT = 0.3;
	const chosen = $derived.by(() => {
		const candidates = arrangements.map(forMode).map(measure);
		return (
			candidates.find((candidate) => candidate.scale >= MIN_COMFORT) ??
			candidates.reduce((best, candidate) => (candidate.scale > best.scale ? candidate : best))
		);
	});

	// Game.svelte only renders the side counter panel on wide layouts, so
	// everywhere else the bet slot has to carry the count itself.
	const counterInBar = $derived(
		stateUi.freeSpinCounterShow &&
			!['desktop', 'landscape'].includes(context.stateLayoutDerived.layoutType()),
	);

	const barHeight = $derived((chosen.height + PANEL_PAD * 2) * chosen.scale);
	const centerX = $derived(canvas.width * 0.5);
	const centerY = $derived(canvas.height - barHeight * 0.5 - MARGIN);

	const menuRow = $derived(chosen.rows.find((row) => row.keys.includes('menu')));
	const menuX = $derived(centerX + (menuRow?.centers.menu ?? 0) * chosen.scale);
	const menuY = $derived(centerY + (menuRow?.y ?? 0) * chosen.scale);
	const useMenu = $derived(!side.ok && !!menuRow);

	// The buy plaque breathes while the game is idle - a slow swell and a warm glow, the
	// way bonus buys invite a tap in the big studios' games - and holds still otherwise.
	const buyVisible = $derived(side.ok && shown('buy') && !stateUi.freeSpinCounterShow);
	const idle = $derived(context.stateXstateDerived.isIdle());
	let breath = $state(0);
	$effect(() => {
		if (!buyVisible || !idle) {
			breath = 0;
			return;
		}
		let raf = 0;
		const start = performance.now();
		const tick = (now: number) => {
			breath = 0.5 - 0.5 * Math.cos(((now - start) / 1000) * Math.PI * 0.8);
			raf = requestAnimationFrame(tick);
		};
		raf = requestAnimationFrame(tick);
		return () => cancelAnimationFrame(raf);
	});
</script>

{#snippet amount(key: string)}
	<LabelPlate width={LABEL_W * 1.06} height={PLATE_H} />
	<Container y={LABEL_SHIFT_Y}>
		{#if key === 'balance'}
			{@render props.amountBalance({ stacked: true })}
		{:else if key === 'win'}
			{@render props.amountWin({ stacked: true })}
		{:else if counterInBar}
			<!-- the shared LabelFreeSpinCounter draws a plate asset this game never shipped -->
			<BarLabel
				label="FREE SPINS"
				value={`${stateUi.freeSpinCounterCurrent} / ${stateUi.freeSpinCounterTotal}`}
			/>
		{:else}
			{@render props.amountBet({ stacked: true })}
		{/if}
	</Container>
{/snippet}

{#snippet spin(size: number)}
	{#if isReplay()}
		<ReplayButton3D {size} />
	{:else}
		<SpinButton3D {size} />
	{/if}
{/snippet}

{#if side.ok}
	<!-- the strip: balance, win and the menu icons, flat along the bottom edge -->
	<Container zIndex={60}>
		<Rectangle
			x={canvas.width * 0.5}
			y={canvas.height - side.stripH * 0.5}
			anchor={0.5}
			width={canvas.width}
			height={side.stripH}
			backgroundColor={0x05090b}
			backgroundAlpha={0.62}
		/>
		<Rectangle
			x={canvas.width * 0.5}
			y={canvas.height - side.stripH}
			anchor={0.5}
			width={canvas.width}
			height={2}
			backgroundColor={0xb89150}
			backgroundAlpha={0.7}
		/>
		<Container x={SIDE_MARGIN} y={canvas.height - side.stripH * 0.5} scale={side.stripScale}>
			{#each ICONS as key, i (key)}
				<Container x={B * 0.5 + i * (B + ICON_GAP)}>
					<BarButton kind={key} />
				</Container>
			{/each}
		</Container>
		<Container x={canvas.width * 0.5} y={canvas.height - side.stripH * 0.5} scale={side.stripScale}>
			{#if shown('balance')}
				<Container x={-STRIP_LABEL_SPACING * 0.5}>
					{@render amount('balance')}
				</Container>
			{/if}
			<Container x={shown('balance') ? STRIP_LABEL_SPACING * 0.5 : 0}>
				{@render amount('win')}
			</Container>
		</Container>
	</Container>

	<!-- the play cluster, right of the tank: bet -/+ over a big spin, autoplay and turbo.
	     A soft shadow pool under it keeps it legible over the trawler and the surf. -->
	<Container zIndex={60} x={side.cx} y={side.cy} scale={side.q}>
		<Sprite
			key="fxGlow"
			anchor={0.5}
			width={CLUSTER_W * 1.45}
			height={CLUSTER_H * 1.5}
			tint={0x000000}
			alpha={0.7}
		/>
		<Container y={-CLUSTER_H * 0.5 + LABEL_H * 0.5}>
			{#if shown('dec')}
				<Container x={-(LABEL_W + B) * 0.5 - SIDE_GAP}>
					<BarButton kind="dec" />
				</Container>
			{/if}
			{@render amount('bet')}
			{#if shown('inc')}
				<Container x={(LABEL_W + B) * 0.5 + SIDE_GAP}>
					<BarButton kind="inc" />
				</Container>
			{/if}
		</Container>
		<Container y={CLUSTER_H * 0.5 - SPIN_BIG * 0.5}>
			{@render spin(SPIN_BIG)}
			{#if shown('auto')}
				<Container x={-(SPIN_BIG + B) * 0.5 - SIDE_GAP} y={SPIN_BIG * 0.18}>
					<BarButton kind="auto" />
				</Container>
			{/if}
			<Container x={(SPIN_BIG + B) * 0.5 + SIDE_GAP} y={SPIN_BIG * 0.18}>
				<BarButton kind="turbo" />
			</Container>
		</Container>
	</Container>

	<!-- the bonus buy, big, in the sky left of the tank (the free-spins HUD takes this
	     spot while it is hidden during free spins) -->
	{#if buyVisible}
		<Container zIndex={60} x={side.lx} y={side.cy} scale={side.q * BUY_K}>
			<Sprite key="fxGlow" anchor={0.5} width={B * 3.6} height={B * 1.9} tint={0x000000} alpha={0.5} />
			<Sprite
				key="fxGlow"
				anchor={0.5}
				width={B * 3.0}
				height={B * 1.5}
				tint={0xffb54a}
				alpha={0.12 + 0.3 * breath}
				blendMode="add"
			/>
			<Container scale={1 + 0.04 * breath}>
				<BarButton kind="buy" />
			</Container>
		</Container>
	{/if}
{:else}
	<Container zIndex={60}>
		<Container x={centerX} y={centerY} scale={chosen.scale}>
			<!-- A riveted iron strap with a brass rim - the tank frame's own materials. Sized in
			the bar's authoring units: a 9-slice draws its corners at texture scale, so it has
			to live inside the scaled container or the corners swamp a small phone bar. -->
			<NineSlice
				key="panel.png"
				width={chosen.width + PANEL_PAD * 2}
				height={chosen.height + PANEL_PAD * 2}
				border={PANEL_BORDER}
			/>

			{#each chosen.rows as row (row.y)}
				{#each row.keys as key (key)}
					<Container x={row.centers[key]} y={row.y}>
						{#if LABEL_KEYS.includes(key)}
							{@render amount(key)}
						{:else if key === 'buy'}
							{#if !stateUi.freeSpinCounterShow}
								<BarButton kind="buy" />
							{/if}
						{:else if key === 'dec' || key === 'inc'}
							{#if !counterInBar}
								<BarButton kind={BUTTON_KEYS[key]} />
							{/if}
						{:else if BUTTON_KEYS[key]}
							<BarButton kind={BUTTON_KEYS[key]} />
						{:else if key === 'spin'}
							{@render spin(SPIN)}
						{/if}
					</Container>
				{/each}
			{/each}
		</Container>
	</Container>
{/if}

{#if useMenu && stateUi.menuOpen}
	<Container zIndex={61}>
		<Rectangle
			eventMode="static"
			cursor="pointer"
			anchor={0.5}
			alpha={0.5}
			backgroundColor={BLACK}
			x={canvas.width * 0.5}
			y={canvas.height * 0.5}
			width={canvas.width}
			height={canvas.height}
			onpointerup={() => (stateUi.menuOpen = false)}
		/>

		<Container x={menuX} y={menuY} scale={chosen.scale}>
			<Container y={-(B + GAP) * 4}>
				<BarButton kind="pay" />
			</Container>
			<Container y={-(B + GAP) * 3}>
				<BarButton kind="rules" />
			</Container>
			<Container y={-(B + GAP) * 2}>
				<BarButton kind="settings" />
			</Container>
			<Container y={-(B + GAP)}>
				<BarButton kind="sound" />
			</Container>
			<Container>
				<BarButton kind="close" />
			</Container>
		</Container>
	</Container>
{/if}

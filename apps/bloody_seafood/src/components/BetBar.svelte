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
	import BarLabel from './bar3d/BarLabel.svelte';
	import LabelPlate from './bar3d/LabelPlate.svelte';
	import { STACKED, STACKED_ROW_H, STACKED_ROW_W, stackedBar } from '../game/barLayout';

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
	// - BOTTOM (portrait, near-square): one row of controls over a slim info strip, sized
	//   first to a fixed share of the screen (game/barLayout.ts) with the board stood in
	//   what is left - filling the band under the board let it take ~40% of a phone.
	// Size follows importance in both: the spin is by far the biggest, the bonus buy next,
	// play -/+ and autoplay/turbo a step down, and the menu icons smallest of all.
	const B = UI_BASE_SIZE;
	const GAP = 46;
	const LABEL_W = 400;
	const LABEL_H = 132;
	const PLATE_H = LABEL_H * 1.12;
	/** play -/+, autoplay and turbo, as a share of a full UI_BASE_SIZE button */
	const STEP_K = 0.85;
	/** rules, paytable, settings, sound */
	const ICON_K = 0.68;

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
	const SPIN_BIG = B * 2.3;
	const STEP = B * STEP_K;
	const SIDE_GAP = 30;
	const CLUSTER_W = Math.max(
		STEP + SIDE_GAP + LABEL_W + SIDE_GAP + STEP,
		STEP + SIDE_GAP + SPIN_BIG + SIDE_GAP + STEP,
	);
	const CLUSTER_H = LABEL_H + GAP + SPIN_BIG;
	const SIDE_MARGIN = 16;
	/** the spin never needs to be bigger than this on screen (px): top-studio desktop size */
	const MAX_SIDE_SCALE = 0.46;
	const MIN_SIDE_SCALE = 0.2;
	/** the buy plaque, relative to BarButton's own buy size (1.9 B wide) */
	const BUY_K = 1.5;

	const STRIP_UNITS = PLATE_H + 24;
	const ICONS = ['rules', 'pay', 'settings', 'sound'] as const;
	const ICON = B * ICON_K;
	const ICON_GAP = 26;
	const ICONS_W = ICONS.length * ICON + (ICONS.length - 1) * ICON_GAP;
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
	const stacked = $derived(stackedBar(canvas));
	const sq = $derived(stacked.scale);
	const S = STACKED;
	const stripCy = $derived(canvas.height - (S.STRIP_H * sq) / 2);
	const rowCy = $derived(canvas.height - (S.STRIP_H + S.ROW_PAD + STACKED_ROW_H / 2) * sq);
	/** row positions from the spin's centre, in bar units */
	const ROW = {
		dec: -(S.SPIN / 2 + S.GAP + S.STEP / 2),
		buy: -(S.SPIN / 2 + S.GAP * 2 + S.STEP + (B * 1.9 * S.BUY_K) / 2),
		inc: S.SPIN / 2 + S.GAP + S.STEP / 2,
		auto: S.SPIN / 2 + S.GAP * 2 + S.STEP + S.SMALL / 2,
		turbo: S.SPIN / 2 + S.GAP * 2.6 + S.STEP + S.SMALL * 1.5,
	};
	/** the strip's amounts: drawn a step down from the plates' size */
	const STRIP_LABEL_K = 0.86;
	const stripLeft = -STACKED_ROW_W / 2;
	const menuStripX = stripLeft + S.ICON / 2;
	const stripAmountsLeft = stripLeft + S.ICON + S.GAP;
	const stripSlot = (STACKED_ROW_W / 2 - stripAmountsLeft) / 3;
	const stripX = (i: number) => stripAmountsLeft + stripSlot * (i + 0.5);

	// A replay only watches one finished round: no balance, no changing the play amount,
	// no bonus purchase or autoplay. The play slot becomes the replay-again button.
	const REPLAY_HIDDEN = ['balance', 'buy', 'dec', 'inc', 'auto'];
	const shown = (key: string) => !(isReplay() && REPLAY_HIDDEN.includes(key));

	// Game.svelte only renders the side counter panel on wide layouts, so
	// everywhere else the bet slot has to carry the count itself.
	const counterInBar = $derived(
		stateUi.freeSpinCounterShow &&
			!['desktop', 'landscape'].includes(context.stateLayoutDerived.layoutType()),
	);

	const menuX = $derived(canvas.width * 0.5 + menuStripX * sq);
	const menuY = $derived(stripCy);
	const useMenu = $derived(!side.ok);

	// The buy plaque breathes while the game is idle - a slow swell and a warm glow, the
	// way bonus buys invite a tap in the big studios' games - and holds still otherwise.
	const buyVisible = $derived(shown('buy') && !stateUi.freeSpinCounterShow);
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

{#snippet amountValue(key: string)}
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
{/snippet}

{#snippet amount(key: string)}
	<LabelPlate width={LABEL_W * 1.06} height={PLATE_H} />
	{@render amountValue(key)}
{/snippet}

{#snippet spin(size: number)}
	{#if isReplay()}
		<ReplayButton3D {size} />
	{:else}
		<SpinButton3D {size} />
	{/if}
{/snippet}

{#snippet step(kind: BarButtonKind)}
	<Container scale={STEP_K}>
		<BarButton {kind} />
	</Container>
{/snippet}

<!-- The bonus buy breathes while the game is idle - a slow swell and a warm glow, the way
     bonus buys invite a tap in the big studios' games - and holds still otherwise. -->
{#snippet buyPlaque()}
	<Sprite key="fxGlow" anchor={0.5} width={B * 3.6} height={B * 1.9} tint={0x000000} alpha={0.5} />
	<Sprite
		key="fxGlow"
		anchor={0.5}
		width={B * 3.0}
		height={B * 1.5}
		tint={0xffb54a}
		alpha={0.18 + 0.4 * breath}
		blendMode="add"
	/>
	<Container scale={1 + 0.05 * breath}>
		<BarButton kind="buy" />
	</Container>
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
				<Container x={ICON * 0.5 + 12 + i * (ICON + ICON_GAP)} scale={ICON_K}>
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
				<Container x={-(LABEL_W + STEP) * 0.5 - SIDE_GAP}>
					{@render step('dec')}
				</Container>
			{/if}
			{@render amount('bet')}
			{#if shown('inc')}
				<Container x={(LABEL_W + STEP) * 0.5 + SIDE_GAP}>
					{@render step('inc')}
				</Container>
			{/if}
		</Container>
		<Container y={CLUSTER_H * 0.5 - SPIN_BIG * 0.5}>
			{@render spin(SPIN_BIG)}
			{#if shown('auto')}
				<Container x={-(SPIN_BIG + STEP) * 0.5 - SIDE_GAP} y={SPIN_BIG * 0.2}>
					{@render step('auto')}
				</Container>
			{/if}
			<Container x={(SPIN_BIG + STEP) * 0.5 + SIDE_GAP} y={SPIN_BIG * 0.2}>
				{@render step('turbo')}
			</Container>
		</Container>
	</Container>

	<!-- the bonus buy, big, in the sky left of the tank (the free-spins HUD takes this
	     spot while it is hidden during free spins) -->
	{#if buyVisible}
		<Container zIndex={60} x={side.lx} y={side.cy} scale={side.q * BUY_K}>
			{@render buyPlaque()}
		</Container>
	{/if}
{:else}
	<Container zIndex={60}>
		<!-- the info strip along the bottom edge, as on desktop -->
		<Rectangle
			x={canvas.width * 0.5}
			y={stripCy}
			anchor={0.5}
			width={canvas.width}
			height={S.STRIP_H * sq}
			backgroundColor={0x05090b}
			backgroundAlpha={0.72}
		/>
		<Rectangle
			x={canvas.width * 0.5}
			y={canvas.height - S.STRIP_H * sq}
			anchor={0.5}
			width={canvas.width}
			height={2}
			backgroundColor={0xb89150}
			backgroundAlpha={0.7}
		/>
		<Container x={canvas.width * 0.5} y={stripCy} scale={sq}>
			<Container x={menuStripX} scale={S.ICON / B}>
				<BarButton kind="menu" />
			</Container>
			{#each ['balance', 'bet', 'win'] as key, i (key)}
				{#if shown(key)}
					<Container x={stripX(i)} scale={STRIP_LABEL_K}>
						{@render amountValue(key)}
					</Container>
				{/if}
			{/each}
		</Container>

		<!-- the control row: spin dead centre, a soft shadow pool keeping it legible -->
		<Container x={canvas.width * 0.5} y={rowCy} scale={sq}>
			<Sprite
				key="fxGlow"
				anchor={0.5}
				width={STACKED_ROW_W * 1.25}
				height={STACKED_ROW_H * 1.6}
				tint={0x000000}
				alpha={0.6}
			/>
			{#if buyVisible}
				<Container x={ROW.buy} scale={S.BUY_K}>
					{@render buyPlaque()}
				</Container>
			{/if}
			{#if shown('dec') && !counterInBar}
				<Container x={ROW.dec}>{@render step('dec')}</Container>
			{/if}
			{@render spin(S.SPIN)}
			{#if shown('inc') && !counterInBar}
				<Container x={ROW.inc}>{@render step('inc')}</Container>
			{/if}
			{#if shown('auto')}
				<Container x={ROW.auto}>{@render step('auto')}</Container>
			{/if}
			<Container x={ROW.turbo}>{@render step('turbo')}</Container>
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

		<!-- the menu fans up from its strip icon, each entry a full-size button -->
		<Container x={menuX + (B * sq) / 2} y={menuY} scale={sq}>
			{#each ['pay', 'rules', 'settings', 'sound'] as kind, i (kind)}
				<Container y={-(B + GAP) * (4 - i) - B * 0.3}>
					<BarButton kind={kind as BarButtonKind} />
				</Container>
			{/each}
			<Container x={-B * 0.5 + S.ICON * 0.5} scale={S.ICON / B}>
				<BarButton kind="close" />
			</Container>
		</Container>
	</Container>
{/if}

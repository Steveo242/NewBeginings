<script lang="ts">
	import { Container, Rectangle } from 'pixi-svelte';
	import { stateUi } from 'state-shared';
	import { BLACK } from 'constants-shared/colors';
	import type { LayoutUiProps } from 'components-ui-pixi/src/types';
	import { UI_BASE_SIZE } from 'components-ui-pixi/src/constants';
	import LabelFreeSpinCounter from 'components-ui-pixi/src/components/LabelFreeSpinCounter.svelte';

	import { getContext } from '../game/context';
	import { BOARD_SIZES } from '../game/constants';
	import BarButton, { type BarButtonKind } from './bar3d/BarButton.svelte';
	import SpinButton3D from './bar3d/SpinButton3D.svelte';
	import NineSlice from './bar3d/NineSlice.svelte';

	const props: LayoutUiProps = $props();
	const context = getContext();

	const canvas = $derived(context.stateLayoutDerived.canvasSizes());
	const main = $derived(context.stateLayoutDerived.mainLayout());

	// The bar is authored once in the shared controls' own coordinate space
	// and scaled by a single factor, so sizes and positions always scale
	// together. Scaling them off different axes is what previously let every
	// control overlap its neighbour on a portrait canvas.
	const SPIN = UI_BASE_SIZE * 1.35;
	const LABEL_W = 430;
	const LABEL_H = 132;
	const GAP = 46;
	const ROW_GAP = 32;
	/** Stacked labels draw downwards from their origin, so lift them to sit centred. */
	const LABEL_SHIFT_Y = -UI_BASE_SIZE * 0.37;

	// Every control is now a rendered 3D button (bar3d/, art from build_ui3d.py) with an
	// icon instead of a word-wrapped caption, so the icon slots are uniform again. The
	// buy-bonus plaque is a wide pill.
	const SLOT_W: Record<string, number> = {
		rules: UI_BASE_SIZE,
		pay: UI_BASE_SIZE,
		settings: UI_BASE_SIZE,
		sound: UI_BASE_SIZE,
		menu: UI_BASE_SIZE,
		auto: UI_BASE_SIZE,
		turbo: UI_BASE_SIZE,
		buy: UI_BASE_SIZE * 1.9,
		dec: UI_BASE_SIZE,
		inc: UI_BASE_SIZE,
		spin: SPIN,
		balance: LABEL_W,
		win: LABEL_W,
		bet: LABEL_W,
	};

	const LABEL_KEYS = ['balance', 'win', 'bet'];
	// The amounts draw navy text, and UiLabel's own `tiled` plate draws an asset key this
	// game has never shipped, so each sits on a rendered cream-enamel plate (brass rim,
	// corner rivets) - the same contrast the flat cream plates gave.
	const BUTTON_KEYS: Record<string, BarButtonKind> = {
		menu: 'menu',
		rules: 'rules',
		pay: 'pay',
		settings: 'settings',
		sound: 'sound',
		buy: 'buy',
		dec: 'dec',
		inc: 'inc',
		auto: 'auto',
		turbo: 'turbo',
	};
	/** 9-slice corner sizes, in texture px (build_ui3d.py panel/plate renders) */
	const PANEL_BORDER = 80;
	const PLATE_BORDER = 50;

	type Row = { keys: string[]; height: number };

	const wideIcons = $derived(
		canvas.width < 1200 ? ['menu'] : ['rules', 'pay', 'settings', 'sound'],
	);

	const arrangements = $derived({
		wide: [
			{
				height: Math.max(SPIN, LABEL_H),
				keys: [
					...wideIcons,
					'buy',
					'balance',
					'win',
					'bet',
					'dec',
					'spin',
					'inc',
					'auto',
					'turbo',
				],
			},
		] as Row[],
		compact: [
			{ height: LABEL_H, keys: ['balance', 'win', 'bet'] },
			{ height: SPIN, keys: ['menu', 'buy', 'dec', 'spin', 'inc', 'auto', 'turbo'] },
		] as Row[],
		stacked: [
			{ height: LABEL_H, keys: ['balance', 'win'] },
			{ height: SPIN, keys: ['menu', 'auto', 'spin', 'turbo', 'buy'] },
			{ height: UI_BASE_SIZE, keys: ['dec', 'bet', 'inc'] },
		] as Row[],
	});

	const WIDTH_RATIO = 0.92;
	const MAX_SCALE = 0.4;
	const MARGIN = 8;

	// The band left under the board is the bar's real height budget. Sizing
	// against that rather than a flat fraction of the canvas is what keeps the
	// bar off the reels - it was covering the bottom rows before. Derived from
	// the board's own layout so it stays right if the board moves.
	const boardBottom = $derived(
		canvas.height * 0.5 +
			(context.stateGameDerived.boardLayout().y + BOARD_SIZES.height * 0.5 - main.height * 0.5) *
				main.scale,
	);
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

		const scale = Math.min(
			(canvas.width * WIDTH_RATIO) / width,
			Math.max(roomBelowBoard, 1) / height,
			MAX_SCALE,
		);

		return { rows: placed, width, height, scale };
	};

	// Prefer the widest arrangement that still tests comfortably, rather than
	// simply the largest controls: once the board leaves a generous band, the
	// two-row split wins on raw scale and a desktop bar that already reads
	// well would fold itself in half for no reason. Only when nothing is
	// comfortable does the biggest win.
	const MIN_COMFORT = 0.3;
	const chosen = $derived.by(() => {
		const candidates = [arrangements.wide, arrangements.compact, arrangements.stacked].map(measure);
		return (
			candidates.find((candidate) => candidate.scale >= MIN_COMFORT) ??
			candidates.reduce((best, candidate) => (candidate.scale > best.scale ? candidate : best))
		);
	});

	const useMenu = $derived(chosen.rows.some((row) => row.keys.includes('menu')));

	// Game.svelte only renders the side counter panel on wide layouts, so
	// everywhere else the play slot has to carry the count itself.
	const counterInBar = $derived(
		stateUi.freeSpinCounterShow &&
			!['desktop', 'landscape'].includes(context.stateLayoutDerived.layoutType()),
	);

	const barHeight = $derived(chosen.height * chosen.scale);
	const centerX = $derived(canvas.width * 0.5);
	const centerY = $derived(canvas.height - barHeight * 0.5 - MARGIN);

	// room for the 3D buttons, whose art (shadow included) is drawn 1.3x their slot
	const PANEL_PAD = 64;

	const menuRow = $derived(chosen.rows.find((row) => row.keys.includes('menu')));
	const menuX = $derived(centerX + (menuRow?.centers.menu ?? 0) * chosen.scale);
	const menuY = $derived(centerY + (menuRow?.y ?? 0) * chosen.scale);
</script>

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
						<!-- oversized: the render carries a shadow margin round the plate itself -->
						<NineSlice key="plate.png" width={SLOT_W[key] * 1.1} height={LABEL_H * 1.25} border={PLATE_BORDER} />
					{/if}
					<Container y={LABEL_KEYS.includes(key) ? LABEL_SHIFT_Y : 0}>
						{#if key === 'buy'}
							{#if !stateUi.freeSpinCounterShow}
								<BarButton kind="buy" />
							{/if}
						{:else if key === 'dec' || key === 'inc'}
							{#if !counterInBar}
								<BarButton kind={BUTTON_KEYS[key]} />
							{/if}
						{:else if BUTTON_KEYS[key]}
							<BarButton kind={BUTTON_KEYS[key]} />
						{:else if key === 'balance'}
							{@render props.amountBalance({ stacked: true })}
						{:else if key === 'win'}
							{@render props.amountWin({ stacked: true })}
						{:else if key === 'bet'}
							{#if counterInBar}
								<LabelFreeSpinCounter stacked />
							{:else}
								{@render props.amountBet({ stacked: true })}
							{/if}
						{:else if key === 'spin'}
							<SpinButton3D size={SPIN} />
						{/if}
					</Container>
				</Container>
			{/each}
		{/each}
	</Container>
</Container>

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
			<Container y={-(UI_BASE_SIZE + GAP) * 4}>
				<BarButton kind="pay" />
			</Container>
			<Container y={-(UI_BASE_SIZE + GAP) * 3}>
				<BarButton kind="rules" />
			</Container>
			<Container y={-(UI_BASE_SIZE + GAP) * 2}>
				<BarButton kind="settings" />
			</Container>
			<Container y={-(UI_BASE_SIZE + GAP)}>
				<BarButton kind="sound" />
			</Container>
			<Container>
				<BarButton kind="close" />
			</Container>
		</Container>
	</Container>
{/if}

<script lang="ts">
	import { Container, Rectangle } from 'pixi-svelte';
	import { stateUi } from 'state-shared';
	import { BLACK } from 'constants-shared/colors';
	import type { LayoutUiProps } from 'components-ui-pixi/src/types';
	import { UI_BASE_SIZE } from 'components-ui-pixi/src/constants';
	import LabelFreeSpinCounter from 'components-ui-pixi/src/components/LabelFreeSpinCounter.svelte';

	import { getContext } from '../game/context';
	import { BOARD_SIZES } from '../game/constants';

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

	// Authored widths, which are not uniform: the four incidental buttons are
	// UI_BASE_SIZE * 1.3, and any button UiButton has no icon asset for draws
	// a text caption that word-wraps at 200. Budgeting UI_BASE_SIZE for those
	// is what left SETTINGS/SOUND ON touching and AUTO SPIN/TURBO running off
	// the right edge.
	const TEXT_CAPTION_W = 200;
	const SLOT_W: Record<string, number> = {
		rules: UI_BASE_SIZE * 1.3,
		pay: UI_BASE_SIZE * 1.3,
		// "SETTINGS" is one unwrappable word ~236 units wide, so its button
		// carries a wider plate than the shared default - see
		// ButtonSettingsWide.svelte.
		settings: 270,
		sound: TEXT_CAPTION_W,
		menu: TEXT_CAPTION_W,
		auto: TEXT_CAPTION_W,
		turbo: TEXT_CAPTION_W,
		buy: UI_BASE_SIZE,
		dec: UI_BASE_SIZE,
		inc: UI_BASE_SIZE,
		spin: SPIN,
		balance: LABEL_W,
		win: LABEL_W,
		bet: LABEL_W,
	};

	const LABEL_KEYS = ['balance', 'win', 'bet'];
	// These three are `bare`, so UiButton draws their caption in navy with no
	// plate behind it - invisible against this bar. The amounts have the same
	// problem: UiLabel's own `tiled` plate draws an asset key this game has
	// never shipped, so they were landing at roughly 1.4:1 on near-black.
	const PLATED_KEYS = [...LABEL_KEYS, 'menu', 'auto', 'turbo'];
	const PLATE_COLOR = 0xe6d8bc;

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

	const PANEL_PAD = 26;

	const menuRow = $derived(chosen.rows.find((row) => row.keys.includes('menu')));
	const menuX = $derived(centerX + (menuRow?.centers.menu ?? 0) * chosen.scale);
	const menuY = $derived(centerY + (menuRow?.y ?? 0) * chosen.scale);
</script>

<Container zIndex={60}>
	<!-- Dark and semi-transparent so the harbour behind it still shows. -->
	<Rectangle
		anchor={0.5}
		x={centerX}
		y={centerY}
		width={(chosen.width + PANEL_PAD * 2) * chosen.scale}
		height={(chosen.height + PANEL_PAD * 2) * chosen.scale}
		borderRadius={(chosen.height + PANEL_PAD * 2) * chosen.scale * 0.18}
		backgroundColor={0x0a1a24}
		backgroundAlpha={0.82}
	/>

	<Container x={centerX} y={centerY} scale={chosen.scale}>
		{#each chosen.rows as row (row.y)}
			{#each row.keys as key (key)}
				<Container x={row.centers[key]} y={row.y}>
					{#if PLATED_KEYS.includes(key)}
						<Rectangle
							anchor={0.5}
							width={SLOT_W[key]}
							height={LABEL_KEYS.includes(key) ? LABEL_H : UI_BASE_SIZE * 0.66}
							borderRadius={UI_BASE_SIZE * 0.18}
							backgroundColor={PLATE_COLOR}
							backgroundAlpha={0.94}
						/>
					{/if}
					<Container y={LABEL_KEYS.includes(key) ? LABEL_SHIFT_Y : 0}>
						{#if key === 'menu'}
							{@render props.buttonMenu({ anchor: 0.5 })}
						{:else if key === 'rules'}
							{@render props.buttonGameRules({ anchor: 0.5 })}
						{:else if key === 'pay'}
							{@render props.buttonPayTable({ anchor: 0.5 })}
						{:else if key === 'settings'}
							{@render props.buttonSettings({ anchor: 0.5 })}
						{:else if key === 'sound'}
							{@render props.buttonSoundSwitch({ anchor: 0.5 })}
						{:else if key === 'buy'}
							{#if !stateUi.freeSpinCounterShow}
								{@render props.buttonBuyBonus({ anchor: 0.5 })}
							{/if}
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
						{:else if key === 'dec'}
							{#if !counterInBar}
								{@render props.buttonDecrease({ anchor: 0.5 })}
							{/if}
						{:else if key === 'inc'}
							{#if !counterInBar}
								{@render props.buttonIncrease({ anchor: 0.5 })}
							{/if}
						{:else if key === 'spin'}
							<Container scale={SPIN / UI_BASE_SIZE}>
								{@render props.buttonBet({ anchor: 0.5 })}
							</Container>
						{:else if key === 'auto'}
							{@render props.buttonAutoSpin({ anchor: 0.5 })}
						{:else if key === 'turbo'}
							{@render props.buttonTurbo({ anchor: 0.5 })}
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
				{@render props.buttonPayTable({ anchor: 0.5 })}
			</Container>
			<Container y={-(UI_BASE_SIZE + GAP) * 3}>
				{@render props.buttonGameRules({ anchor: 0.5 })}
			</Container>
			<Container y={-(UI_BASE_SIZE + GAP) * 2}>
				{@render props.buttonSettings({ anchor: 0.5 })}
			</Container>
			<Container y={-(UI_BASE_SIZE + GAP)}>
				{@render props.buttonSoundSwitch({ anchor: 0.5 })}
			</Container>
			<Container>
				{@render props.buttonMenuClose({ anchor: 0.5 })}
			</Container>
		</Container>
	</Container>
{/if}

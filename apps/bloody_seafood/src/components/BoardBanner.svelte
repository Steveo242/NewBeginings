<script lang="ts">
	import { BaseSprite, Container, Sprite } from 'pixi-svelte';

	import { getContext } from '../game/context';
	import { BOARD_SIZES, LOGO_ASPECT } from '../game/constants';
	import { BEAT_MS } from '../game/tempo';
	import { bloodDropTexture } from '../game/fxTextures';

	const context = getContext();

	const main = $derived(context.stateLayoutDerived.mainLayout());
	const board = $derived(context.stateGameDerived.boardLayout());

	/** logo3d.webp's aspect: the 3D logo (bs-render build_logo3d.py), tight-cropped. */
	const BANNER_ASPECT = LOGO_ASPECT;
	const MARGIN = 10;
	/** Never let the banner crowd the reels by outgrowing the board itself. */
	const MAX_WIDTH_RATIO = 0.92;

	// The board sits above centre, so the band over it is what is left between
	// the top of the design space and the board's own top edge. Fit the banner
	// to that band rather than to a fixed size, so it can never ride down over
	// the reels on a short canvas - it just gets smaller.
	const boardTop = $derived(board.y - BOARD_SIZES.height * 0.5);
	const available = $derived(Math.max(boardTop - MARGIN * 2, 0));

	const height = $derived(
		Math.min(available, (BOARD_SIZES.width * MAX_WIDTH_RATIO) / BANNER_ASPECT),
	);
	const width = $derived(height * BANNER_ASPECT);
	const centerY = $derived(boardTop - MARGIN - height * 0.5);

	// The title bleeds in time with the music: BLOODY throbs scarlet on every beat like a
	// heartbeat, and the six drips under it take turns swelling a drop and letting it fall,
	// two beats per drip cycle, staggered so a drop is always forming somewhere.
	/** logo3d.webp's own pixel space (1976 x 796): the drip tips, measured off the art */
	const LOGO_W = 1976;
	const LOGO_H = 796;
	const TIPS = [
		[294, 486],
		[519, 424],
		[791, 406],
		[1138, 436],
		[1467, 536],
		[1754, 481],
	] as const;
	/** one drip's cycle, in beats: swell at the tip, then fall and fade */
	const CYCLE = 2;
	const SWELL = 0.55;
	const FALL_PX = 380;

	let now = $state(performance.now());
	$effect(() => {
		let raf = 0;
		const tick = (t: number) => {
			now = t;
			raf = requestAnimationFrame(tick);
		};
		raf = requestAnimationFrame(tick);
		return () => cancelAnimationFrame(raf);
	});
	const beats = $derived(now / BEAT_MS);
	/** sharp attack on the beat, decaying through it */
	const throb = $derived(Math.exp(-(beats % 1) * 4.5));
	const unit = $derived(width / LOGO_W);

	const drops = $derived(
		TIPS.map(([x, y], i) => {
			// drips fire in a scrambled order so it doesn't read as a left-to-right wave
			const offset = ((i * 4) % TIPS.length) / TIPS.length;
			const u = (beats / CYCLE + offset) % 1;
			const swell = Math.min(1, u / (SWELL / CYCLE));
			const fallT = Math.max(0, u - SWELL / CYCLE) / (1 - SWELL / CYCLE);
			return {
				x: (x - LOGO_W / 2) * unit,
				y: (y - LOGO_H / 2 + FALL_PX * fallT * fallT) * unit,
				size: 62 * unit * (0.35 + 0.65 * swell) * (1 + 0.25 * fallT),
				stretch: 1 + 0.5 * fallT,
				alpha: fallT > 0.6 ? 1 - (fallT - 0.6) / 0.4 : 1,
			};
		}),
	);
</script>

{#if height > 1}
	<Container x={board.x} y={centerY}>
		<Sprite key="titlePlaqueBoard" anchor={0.5} {width} {height} />
		<!-- the heartbeat: a scarlet bloom over the red letters only -->
		<Sprite key="logoBlood" anchor={0.5} {width} {height} alpha={0.55 * throb} blendMode="add" />
		{#each drops as drop, i (i)}
			<BaseSprite
				texture={bloodDropTexture()}
				anchor={{ x: 0.5, y: 0.1 }}
				x={drop.x}
				y={drop.y - drop.size * 0.15}
				width={drop.size}
				height={drop.size * 1.5 * drop.stretch}
				alpha={drop.alpha}
			/>
		{/each}
	</Container>
{/if}

<script lang="ts">
	// One anticipating reel (a scatter short of the feature): two hawsers drop down the
	// column's edges and strain - thrumming, the column between them flushed blood-red -
	// while the reel drops, matching the rope audio (sfx_rope_taut / _strain / _snap).
	// The hawsers are a seamless 3D render (bs-render build_rope3d.py, the symbol studio's
	// lights) bent along a PIXI.MeshRope; this used to be the sample game's anticipation spine. The phases keep
	// its names: intro (the ropes run down the column), loop (strain), out (they go slack
	// and fade once the reel stops), then oncomplete.
	import * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { getContextParent } from 'pixi-svelte';
	import { stateBetDerived } from 'state-shared';

	import { getContext } from '../game/context';
	import type { Reel } from '../game/stateGame.svelte';
	import { REEL_PADDING, SYMBOL_SIZE } from '../game/constants';

	type Props = {
		reel: Reel;
		oncomplete: () => void;
	};

	const props: Props = $props();
	const context = getContext();
	const parent = getContextParent();

	type AnimationName = 'anticipation_intro' | 'anticipation_loop' | 'anticipation_out';
	let animationName: AnimationName = 'anticipation_intro';

	$effect(() => {
		if (props.reel.reelState.motion === 'stopped' && animationName !== 'anticipation_out') {
			animationName = 'anticipation_out';
			phaseT = 0;
		}
	});

	// the column's CENTRE (getSymbolX places symbols at SYMBOL_SIZE * (reel + REEL_PADDING))
	const reelCentre = $derived(
		context.stateGameDerived.boardLayout().x -
			context.stateGameDerived.boardLayout().width * 0.5 +
			(props.reel.reelIndex + REEL_PADDING) * SYMBOL_SIZE,
	);
	const boardTop = $derived(
		context.stateGameDerived.boardLayout().y - context.stateGameDerived.boardLayout().height * 0.5,
	);

	const INTRO_MS = 320;
	const OUT_MS = 280;
	const HALF = SYMBOL_SIZE * 0.5;
	const ROPE_W = SYMBOL_SIZE * 0.075;

	const root = new PIXI.Container();
	const mask = new PIXI.Graphics();
	const wash = new PIXI.Graphics();
	const motes = new PIXI.Graphics();
	motes.blendMode = 'add';
	root.addChild(mask, wash, motes);

	// The rope texture is 256 px thick; each MeshRope sits in a container scaled down to
	// ROPE_SCALE so it draws ROPE_W * 1.5 thick, its points laid out in that container's
	// units. textureScale 1 repeats the texture along the length at its own aspect.
	const ROPE_SCALE = (ROPE_W * 1.5) / 256;
	const ROPE_N = 24;
	type Rope = { holder: PIXI.Container; mesh: PIXI.MeshRope; points: PIXI.Point[] };
	const ropeTex = context.stateApp.loadedAssets?.fxRope as PIXI.Texture | undefined;
	if (ropeTex) ropeTex.source.addressMode = 'repeat';
	const makeRope = (): Rope | undefined => {
		if (!ropeTex) return undefined;
		const points = Array.from({ length: ROPE_N }, (_, i) => new PIXI.Point(0, i));
		const mesh = new PIXI.MeshRope({ texture: ropeTex, points, textureScale: 1 });
		const holder = new PIXI.Container();
		holder.scale.set(ROPE_SCALE);
		holder.addChild(mesh);
		root.addChild(holder);
		return { holder, mesh, points };
	};
	const ropePair = [makeRope(), makeRope()];
	root.mask = mask;
	parent.addToParent(root);

	type Mote = { x: number; y: number; v: number; r: number; life: number; age: number };
	let moteList: Mote[] = [];
	let phaseT = 0;
	let time = 0;
	let done = false;

	const washFill = new PIXI.FillGradient({
		type: 'linear',
		start: { x: 0, y: 0 },
		end: { x: 1, y: 0 },
		textureSpace: 'local',
		colorStops: [
			{ offset: 0, color: 'rgba(170,10,22,0.55)' },
			{ offset: 0.22, color: 'rgba(120,6,14,0.12)' },
			{ offset: 0.78, color: 'rgba(120,6,14,0.12)' },
			{ offset: 1, color: 'rgba(170,10,22,0.55)' },
		],
	});

	/** a hawser down x from y0 for len px, thrumming by amp (canvas units) */
	const layRope = (r: Rope | undefined, x: number, y0: number, len: number, amp: number, phase: number, alpha: number) => {
		if (!r) return;
		const L = Math.max(len, 2);
		r.points.forEach((p, i) => {
			const u = i / (ROPE_N - 1);
			const sway = Math.sin(u * Math.PI) * amp * Math.sin(time / 38 + phase);
			p.set((x + sway) / ROPE_SCALE, (y0 + u * L) / ROPE_SCALE);
		});
		r.holder.alpha = alpha;
	};

	const tick = () => {
		const app = context.stateApp.pixiApplication;
		if (!app) return;
		const dt = app.ticker.deltaMS * (stateBetDerived.timeScale() || 1);
		time += dt;
		phaseT += dt;
		const H = context.stateGameDerived.boardLayout().height;
		const left = reelCentre - HALF;
		const right = reelCentre + HALF;

		let level = 1;
		let reach = 1;
		if (animationName === 'anticipation_intro') {
			reach = Math.min(1, phaseT / INTRO_MS);
			level = reach;
			if (phaseT >= INTRO_MS) {
				animationName = 'anticipation_loop';
				phaseT = 0;
			}
		} else if (animationName === 'anticipation_out') {
			level = Math.max(0, 1 - phaseT / OUT_MS);
			if (level <= 0 && !done) {
				done = true;
				props.oncomplete();
			}
		}
		// the strain swells and eases on a two-beat cycle (~90 BPM, game/tempo.ts)
		const strain = 0.6 + 0.4 * Math.sin(time / 667);
		const amp = (animationName === 'anticipation_out' ? 6 : 1.6 + 1.6 * strain) * level;

		mask.clear().rect(left, boardTop, SYMBOL_SIZE, H).fill(0xffffff);
		wash.clear().rect(left, boardTop, SYMBOL_SIZE, H).fill(washFill);
		wash.alpha = level * (0.7 + 0.3 * strain);

		const len = H * (1 - (1 - reach) ** 2);
		layRope(ropePair[0], left + ROPE_W, boardTop, len, amp, 0, level);
		layRope(ropePair[1], right - ROPE_W, boardTop, len, amp, 1.7, level);

		// fibres and blood motes drifting up the column
		if (animationName !== 'anticipation_out' && Math.random() < dt / 70) {
			moteList.push({
				x: left + SYMBOL_SIZE * (0.15 + 0.7 * Math.random()),
				y: boardTop + H,
				v: SYMBOL_SIZE * (0.0012 + 0.0012 * Math.random()),
				r: SYMBOL_SIZE * (0.012 + 0.02 * Math.random()),
				life: 900 + 700 * Math.random(),
				age: 0,
			});
		}
		motes.clear();
		moteList = moteList.filter((m) => (m.age += dt) < m.life);
		for (const m of moteList) {
			m.y -= m.v * dt;
			const a = Math.sin((m.age / m.life) * Math.PI) * level;
			motes.circle(m.x + Math.sin(m.age / 180) * 3, m.y, m.r).fill({ color: 0xff4a3a, alpha: 0.5 * a });
		}
	};
	context.stateApp.pixiApplication?.ticker.add(tick);

	onDestroy(() => {
		context.stateApp.pixiApplication?.ticker.remove(tick);
		root.destroy({ children: true });
	});
</script>

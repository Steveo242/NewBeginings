<script lang="ts">
	import * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { getContextParent } from 'pixi-svelte';
	import { stateBetDerived } from 'state-shared';

	import { getContext } from '../game/context';

	// The celebration tiers hit harder as they climb (screen space, over the dim, under the
	// plaque): a camera shake as the title slams down, and a sweep of blood and seawater
	// flung across the screen. MAX WIN also has the shark breach the tank (SharkBreach).
	// Code VFX only: pools of droplet and splat Graphics, no filters, gone after ~2.6 s.
	type Props = { alias: string };
	const props: Props = $props();

	const TIER: Record<string, { shake: number; shakeMs: number; drops: number; splats: number }> = {
		big: { shake: 11, shakeMs: 520, drops: 45, splats: 4 },
		superwin: { shake: 15, shakeMs: 620, drops: 70, splats: 6 },
		mega: { shake: 21, shakeMs: 760, drops: 100, splats: 9 },
		epic: { shake: 27, shakeMs: 900, drops: 130, splats: 12 },
		max: { shake: 36, shakeMs: 1150, drops: 170, splats: 16 },
	};
	const tier = TIER[props.alias] ?? TIER.big;

	const context = getContext();
	const parent = getContextParent();
	const root = new PIXI.Container();
	parent.addToParent(root);
	const app = context.stateApp.pixiApplication;
	const speed = Math.max(1, stateBetDerived.timeScale());
	const rand = (a: number, b: number) => a + Math.random() * (b - a);

	const { width: W, height: H } = context.stateLayoutDerived.canvasSizes();
	const k = H / 1080; // shake and droplet sizes follow the screen
	const fromLeft = Math.random() < 0.5;

	// blood heavy, seawater lighter and paler. Each drop is a teardrop (round head, tail
	// trailing along its flight) with a wet highlight - plain ellipses read as confetti.
	const teardrop = (body: number, alpha: number, hi: number) =>
		new PIXI.Graphics()
			.poly([1, 0, 0.7, 0.62, 0, 0.8, -0.8, 0.45, -3.2, 0, -0.8, -0.45, 0, -0.8, 0.7, -0.62])
			.fill({ color: body, alpha })
			.circle(0.35, -0.3, 0.28)
			.fill({ color: hi, alpha: alpha * 0.7 });
	const drops = Array.from({ length: tier.drops }, () => {
		const blood = Math.random() < 0.7;
		const g = blood ? teardrop(0x6e0508, 0.92, 0xd0383e) : teardrop(0xcfeaff, 0.5, 0xffffff);
		g.visible = false;
		root.addChild(g);
		const vx = rand(0.8, 1.5) * W * (fromLeft ? 1 : -1);
		return {
			g,
			delay: rand(0, 380),
			x: fromLeft ? rand(-0.08, 0.02) * W : rand(0.98, 1.08) * W,
			y: rand(0.08, 0.92) * H,
			vx,
			vy: rand(-0.55, 0.15) * H,
			size: rand(5, blood ? 15 : 10) * k,
			life: rand(1300, 2100),
		};
	});

	// blood splats that hit the screen (the glass of the camera), hang and slide down - the
	// sweep's mark that stays a beat after the drops have flown past
	const splats = Array.from({ length: tier.splats }, () => {
		const g = new PIXI.Graphics();
		const r = rand(14, 34) * k;
		g.circle(0, 0, r).fill({ color: 0x6a0408, alpha: 0.88 });
		for (let i = 0; i < 9; i++) {
			const a = Math.random() * Math.PI * 2;
			const d = r * rand(0.8, 1.9);
			g.circle(Math.cos(a) * d, Math.sin(a) * d, r * rand(0.12, 0.38)).fill({ color: 0x7c070c, alpha: 0.85 });
		}
		g.circle(-r * 0.3, -r * 0.35, r * 0.28).fill({ color: 0xc8343a, alpha: 0.5 }); // wet highlight
		g.visible = false;
		root.addChild(g);
		return { g, x: rand(0.06, 0.94) * W, y: rand(0.08, 0.8) * H, delay: rand(180, 650), slide: rand(18, 60) * k, r };
	});

	const stage = app?.stage;
	const home = stage ? { x: stage.x, y: stage.y } : { x: 0, y: 0 };
	let t = 0;
	const tick = (ticker: PIXI.Ticker) => {
		const dt = ticker.deltaMS * speed;
		t += dt;
		// shake: starts as the title slams (~120 ms), decays out
		if (stage) {
			const u = (t - 120) / tier.shakeMs;
			if (u > 0 && u < 1) {
				const a = tier.shake * k * (1 - u) ** 2;
				stage.position.set(home.x + rand(-a, a), home.y + rand(-a, a));
			} else stage.position.set(home.x, home.y);
		}
		let alive = false;
		for (const d of drops) {
			const age = t - d.delay;
			if (age < 0) {
				alive = true;
				continue;
			}
			const u = age / d.life;
			if (u >= 1) {
				d.g.visible = false;
				continue;
			}
			alive = true;
			const s = age / 1000;
			const vy = d.vy + 1.4 * H * s;
			d.g.visible = true;
			d.g.position.set(d.x + d.vx * s, d.y + d.vy * s + 0.7 * H * s * s);
			d.g.rotation = Math.atan2(vy, d.vx);
			const stretch = 1 + Math.min(1.2, Math.hypot(d.vx, vy) / (H * 1.5));
			d.g.scale.set(d.size * stretch * (1 - u * 0.3), d.size * (1 - u * 0.3));
			d.g.alpha = Math.min(1, (1 - u) * 3);
		}
		for (const sp of splats) {
			const age = t - sp.delay;
			sp.g.visible = age > 0 && age < 2600;
			if (!sp.g.visible) {
				if (age <= 0) alive = true;
				continue;
			}
			alive = true;
			// slaps on (overshoot), hangs, slides down as it fades
			const pop = age < 90 ? 0.6 + (age / 90) * 0.55 : age < 180 ? 1.15 - ((age - 90) / 90) * 0.15 : 1;
			sp.g.scale.set(pop, pop * (1 + Math.max(0, age - 600) / 4000));
			sp.g.position.set(sp.x, sp.y + (Math.max(0, age - 500) / 2000) * sp.slide);
			sp.g.alpha = age < 1600 ? 1 : 1 - (age - 1600) / 1000;
		}
		if (!alive && t > tier.shakeMs + 200) app?.ticker.remove(tick);
	};
	app?.ticker.add(tick);

	onDestroy(() => {
		app?.ticker.remove(tick);
		stage?.position.set(home.x, home.y);
		root.destroy({ children: true });
	});
</script>

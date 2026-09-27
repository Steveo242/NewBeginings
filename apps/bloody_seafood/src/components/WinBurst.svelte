<script lang="ts">
	import { Graphics } from 'pixi-svelte';
	import { onMount } from 'svelte';

	// A one-shot burst behind a win banner: blood droplets and brass sparks thrown out
	// from the plaque, falling under gravity and fading. Drawn as vector dots/streaks
	// each frame (a few dozen shapes - cheaper than a particle texture pipeline).
	type Props = { count?: number; radius?: number; strength?: number };
	const props: Props = $props();

	type P = { x: number; y: number; vx: number; vy: number; r: number; life: number; spark: boolean };
	const N = props.count ?? 64;
	const R = props.radius ?? 260;
	const K = props.strength ?? 1;
	const DURATION = 1.4;

	const parts: P[] = Array.from({ length: N }, () => {
		const a = Math.random() * Math.PI * 2;
		const sp = (170 + Math.random() * 300) * K;
		const spark = Math.random() < 0.45;
		return {
			x: Math.cos(a) * R * 0.35,
			y: Math.sin(a) * R * 0.18,
			vx: Math.cos(a) * sp,
			vy: Math.sin(a) * sp * 0.7 - 180 * K,
			r: spark ? 4 + Math.random() * 4 : 8 + Math.random() * 12,
			life: 0.75 + Math.random() * 0.25,
			spark,
		};
	});

	let t = $state(0);
	onMount(() => {
		const start = performance.now();
		let raf = 0;
		const loop = (now: number) => {
			t = (now - start) / 1000;
			if (t < DURATION) raf = requestAnimationFrame(loop);
		};
		raf = requestAnimationFrame(loop);
		return () => cancelAnimationFrame(raf);
	});

	const G = 620;
	const draw = (g: any) => {
		g.clear();
		for (const p of parts) {
			const life = t / (DURATION * p.life);
			if (life >= 1) continue;
			const x = p.x + p.vx * t;
			const y = p.y + p.vy * t + 0.5 * G * t * t;
			const alpha = 1 - life * life;
			if (p.spark) {
				// a short streak along its velocity: reads as a hot metal spark
				const vx = p.vx, vy = p.vy + G * t;
				const tail = 0.05;
				g.moveTo(x, y).lineTo(x - vx * tail, y - vy * tail).stroke({ width: p.r, color: 0xffd27a, alpha, cap: 'round' });
			} else {
				g.circle(x, y, p.r * (1 - life * 0.3)).fill({ color: 0x8a0710, alpha });
				g.circle(x - p.r * 0.3, y - p.r * 0.3, p.r * 0.3).fill({ color: 0xff6a5a, alpha: alpha * 0.6 });
			}
		}
	};
</script>

<!-- draw reads `t`, so Graphics' own draw effect re-runs every frame -->
<Graphics {draw} />

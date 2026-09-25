<script lang="ts">
	import * as PIXI from 'pixi.js';
	import { onDestroy } from 'svelte';
	import { getContextParent } from 'pixi-svelte';

	import { getContext } from '../game/context';

	type Props = { x: number; y: number; width: number; height: number };
	const props: Props = $props();

	const context = getContext();
	const parent = getContextParent();
	const root = new PIXI.Container();
	parent.addToParent(root);

	// two drifting caustic sheets at different scales, wobbled by a scrolling
	// noise map so the webbing never reads as a fixed pattern
	let layers: PIXI.TilingSprite[] = [];
	let noise: PIXI.Sprite | undefined;
	let t = 0;
	const tick = (ticker: PIXI.Ticker) => {
		t += ticker.deltaMS;
		if (layers.length < 2 || !noise) return;
		layers[0].tilePosition.set(t * 0.012, t * 0.02);
		layers[1].tilePosition.set(-t * 0.009, t * 0.014);
		noise.position.set(-(t * 0.02) % 512, -(t * 0.015) % 512);
	};

	const applyLayout = () => {
		root.position.set(props.x, props.y);
		for (const s of layers) {
			s.width = props.width;
			s.height = props.height;
		}
	};

	$effect(() => {
		const loaded = context.stateApp.loadedAssets;
		if (layers.length || !loaded?.fxCaustics || !loaded?.fxNoise) return;
		const caustics = loaded.fxCaustics as PIXI.Texture;
		const noiseTex = loaded.fxNoise as PIXI.Texture;
		caustics.source.addressMode = 'repeat';
		noiseTex.source.addressMode = 'repeat';
		for (const [scale, alpha] of [[0.9, 0.1], [1.45, 0.07]] as const) {
			const s = new PIXI.TilingSprite({ texture: caustics, width: 10, height: 10 });
			s.tileScale.set(scale);
			s.alpha = alpha;
			s.tint = 0x9ff5ea;
			s.blendMode = 'add';
			root.addChild(s);
			layers.push(s);
		}
		noise = new PIXI.Sprite(noiseTex);
		noise.renderable = false;
		noise.scale.set(2);
		root.addChild(noise);
		root.filters = [new PIXI.DisplacementFilter({ sprite: noise, scale: 14 })];
		context.stateApp.pixiApplication?.ticker.add(tick);
		// sizes may have been applied before the textures existed
		applyLayout();
	});

	$effect(applyLayout);

	onDestroy(() => context.stateApp.pixiApplication?.ticker.remove(tick));
</script>

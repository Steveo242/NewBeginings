<script lang="ts">
	import * as PIXI from 'pixi.js';
	import { onMount, onDestroy, type Snippet } from 'svelte';
	import { devicePixelRatio } from 'svelte/reactivity/window';

	import { getContextApp } from '../context.svelte';
	import { preloadFont } from '../utils.svelte';

	type Props = { children: Snippet };

	const props: Props = $props();
	const context = getContextApp();

	let wrap: HTMLDivElement;
	let initialised = $state(false);

	const initialiseApplication = async () => {
		PIXI.Assets.reset();

		await preloadFont();
		context.stateApp.pixiApplication = new PIXI.Application<PIXI.Renderer<HTMLCanvasElement>>();
		// a game may override renderer options before init (e.g. a low-memory phone path:
		// WebGL instead of WebGPU, no MSAA, a capped resolution) via globalThis.__PIXI_INIT
		const overrides = (globalThis as { __PIXI_INIT?: Partial<PIXI.ApplicationOptions> }).__PIXI_INIT ?? {};
		await context.stateApp.pixiApplication.init({
			autoDensity: true,
			backgroundAlpha: 0,
			hello: true,
			multiView: false,
			antialias: true,
			clearBeforeRender: true,
			preference: 'webgpu',
			powerPreference: 'high-performance',
			resolution: devicePixelRatio.current,
			resizeTo: window,
			...overrides,
		});

		wrap.appendChild(context.stateApp.pixiApplication.canvas);

		// out of graphics memory (common on phones): say so on screen instead of a black page
		context.stateApp.pixiApplication.canvas.addEventListener('webglcontextlost', (event) => {
			event.preventDefault();
			const note = document.createElement('div');
			note.style.cssText =
				'position:fixed;inset:0;display:flex;align-items:center;justify-content:center;z-index:99999;' +
				'background:rgba(0,0,0,.85);color:#fff;font:16px/1.4 sans-serif;text-align:center;padding:24px';
			note.textContent = 'The graphics engine was stopped by the device (out of graphics memory). Tap to reload.';
			note.addEventListener('click', () => location.reload());
			document.body.appendChild(note);
		});

		// to prevent that you can't scroll the page with touch on the canvas. https://github.com/pixijs/pixijs/issues/4824
		context.stateApp.pixiApplication.renderer.events.autoPreventDefault = false;
		context.stateApp.pixiApplication.renderer.canvas.style.touchAction = 'auto';
	};

	onMount(async () => {
		try {
			if (!initialised) await initialiseApplication();
			initialised = true;
		} catch (error) {
			console.error(error);
		}
	});

	onDestroy(() => {
		if (context.stateApp.pixiApplication) {
			context.stateApp.pixiApplication.destroy();
		}
	});
</script>

<div bind:this={wrap}>
	{#if initialised}
		{@render props.children()}
	{/if}
</div>

<script lang="ts">
	import type { Snippet } from 'svelte';
	import * as PIXI from 'pixi.js';

	import { getContextApp } from '../context.svelte';
	import { getProcessed, loadBasisTwin, withTimeout } from '../assetLoad';
	import type { LoadedAssets, RawAsset } from '../types';

	type Props = { children: Snippet };

	const props: Props = $props();
	const context = getContextApp();

	let preLoaded = $state(false);

	const assetNameList = $derived(
		context.stateApp.assets
			? Object.keys(context.stateApp.assets).filter(
					(key) =>
						Boolean(context.stateApp.assets?.[key].preload) === false &&
						!context.stateApp.assets?.[key].lazy,
				)
			: [],
	);

	const preAssetNameList = $derived(
		context.stateApp.assets
			? Object.keys(context.stateApp.assets).filter(
					(key) => context.stateApp.assets?.[key].preload === true,
				)
			: [],
	);

	let counter = 0;

	// On-screen load diagnostics (no DevTools on a phone / the Stake frame): every asset in
	// flight is tracked; only a genuine stall - loading still unfinished after 12 s - shows a
	// panel over the loading screen listing what is pending and the errors seen so far, so it
	// can be photographed. It removes itself once loading completes. Errors otherwise only go
	// to the console. ?diag=1 is the verbose mode: every error, at any time, on screen.
	const verbose =
		typeof location !== 'undefined' && new URLSearchParams(location.search).get('diag') === '1';
	const pending = new Map<string, number>();
	const problems: string[] = [];
	let panel: HTMLDivElement | undefined;
	let stalled = false;
	const show = () => {
		if (typeof document === 'undefined') return;
		if (!panel) {
			panel = document.createElement('div');
			panel.style.cssText =
				'position:fixed;left:8px;right:8px;bottom:8px;max-height:45%;overflow:auto;z-index:99999;' +
				'background:rgba(0,0,0,.85);color:#ffd36a;font:12px/1.35 monospace;padding:8px;white-space:pre-wrap;pointer-events:none';
			document.body.appendChild(panel);
		}
		const now = performance.now();
		const waiting = [...pending.entries()].map(([k, t]) => `  ${k} (${((now - t) / 1000).toFixed(0)} s)`);
		panel.textContent =
			`LOAD DIAGNOSTICS - ${counter}/${assetNameList.length} done\n` +
			(waiting.length ? `still loading (${waiting.length}):\n${waiting.join('\n')}\n` : '') +
			(problems.length ? `errors:\n${problems.map((p) => '  ' + p).join('\n')}` : '');
	};
	const note = (msg: string) => {
		problems.push(msg.slice(0, 300));
		console.warn('[diag]', msg);
		if (verbose || (stalled && !context.stateApp.loaded)) show();
	};
	if (typeof window !== 'undefined') {
		window.addEventListener('error', (e) => note('error: ' + (e.message || e.type) + (e.filename ? ` @ ${e.filename.split('/').pop()}:${e.lineno}` : '')));
		window.addEventListener('unhandledrejection', (e) => note('rejection: ' + String((e.reason && (e.reason.stack || e.reason.message)) || e.reason)));
		const timer = setInterval(() => {
			if (context.stateApp.loaded) {
				clearInterval(timer);
				if (panel && !verbose) {
					panel.remove();
					panel = undefined;
				}
				return;
			}
			stalled = true;
			show();
		}, 12000);
	}

	const onProgress = (value: number) => {
		if (preLoaded && value === 1) {
			counter = counter + 1;
			const ratio = counter / assetNameList.length;
			context.stateApp.loadingProgress = ratio * 100;
		}
	};

	const loadAssets = async (nameList: string[]) => {
		const loadedAssetsArray = await Promise.all(
			nameList.map(async (key) => {
				pending.set(key, performance.now());
				try {
					const { type, src, basis } = context.stateApp.assets![key];
					const loadSrc =
						type === 'spine' ? Object.values(src).filter((item) => typeof item === 'string') : src;
					// a hard cap per asset: one that never settles (a stalled request, a decoder
					// that never answers) is logged and skipped instead of freezing the loader
					const rawAsset = await withTimeout(
						basis
							? loadBasisTwin(src as string, onProgress)
							: PIXI.Assets.load<RawAsset>(loadSrc, onProgress),
						60000,
						key,
					);
					const processed = getProcessed({ key, rawAsset, type, src });
					return processed;
				} catch (error) {
					console.error(error);
					note(`${key}: ${error instanceof Error ? error.message : String(error)}`);
				} finally {
					pending.delete(key);
				}
			}),
		);

		return loadedAssetsArray.reduce(
			(acc, cur) => ({
				...acc,
				...cur,
			}),
			{} as LoadedAssets,
		);
	};

	$effect(() => {
		if (!preLoaded) {
			(async () => {
				if (preAssetNameList.length > 0) {
					const preLoadedAssets = await loadAssets(preAssetNameList);
					if (preLoadedAssets) context.stateApp.loadedAssets = preLoadedAssets;
				}
				preLoaded = true;
			})();
		}
	});

	$effect(() => {
		if (!context.stateApp.loaded && preLoaded) {
			(async () => {
				if (assetNameList.length > 0) {
					const postLoadedAssets = await loadAssets(assetNameList);
					if (postLoadedAssets)
						context.stateApp.loadedAssets = {
							...context.stateApp.loadedAssets,
							...postLoadedAssets,
						};
				}
				context.stateApp.loaded = true;
			})();
		}
	});
</script>

{#if preLoaded}
	{@render props.children()}
{/if}

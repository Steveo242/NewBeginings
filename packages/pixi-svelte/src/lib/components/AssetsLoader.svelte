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
	// flight is tracked, and stalls and errors are logged to the console (and from there the
	// game's persistent error log). On screen only with ?diag=1: a panel listing what is
	// pending and every error, so it can be photographed.
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
		if (verbose) show();
	};
	if (typeof window !== 'undefined') {
		window.addEventListener('error', (e) => note('error: ' + (e.message || e.type) + (e.filename ? ` @ ${e.filename.split('/').pop()}:${e.lineno}` : '')));
		window.addEventListener('unhandledrejection', (e) => note('rejection: ' + String((e.reason && (e.reason.stack || e.reason.message)) || e.reason)));
		// v5.9: nothing on screen in normal play. The panel used to flash up at a 12 s stall
		// and vanish when loading completed - the small dark box Steve saw and couldn't catch.
		// A stall is now logged (console + the game's persistent error log, Ctrl+Shift+D) at
		// LOG_S; the panel is ?diag=1 only (from SHOW_S). This timer runs for the initial load
		// only - it stops at 'loaded'; lazy win sheets never come through here.
		const LOG_S = 12;
		const SHOW_S = 30;
		const started = performance.now();
		let logged = false;
		const timer = setInterval(() => {
			const secs = (performance.now() - started) / 1000;
			if (context.stateApp.loaded) {
				clearInterval(timer);
				if (logged) console.warn(`[diag] slow load finished after ${secs.toFixed(0)} s`);
				if (panel && !verbose) {
					panel.remove();
					panel = undefined;
				}
				return;
			}
			if (secs >= LOG_S && !logged) {
				logged = true;
				console.warn(
					`[diag] load stall (${LOG_S} s): still loading ` +
						([...pending.keys()].join(', ') || 'nothing pending') +
						(problems.length ? ' | errors: ' + problems.join(' | ') : ''),
				);
			}
			if (secs >= SHOW_S) {
				stalled = true;
				if (verbose) show();
			}
		}, 3000);
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

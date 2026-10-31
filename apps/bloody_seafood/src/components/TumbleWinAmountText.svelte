<script lang="ts">
	import WinAmountText from './WinAmountText.svelte';
	import { Container } from 'pixi-svelte';
	import { Tween } from 'svelte/motion';
	import { backOut, cubicOut } from 'svelte/easing';
	import { bookEventAmountToCurrencyString } from 'utils-shared/amount';

	import { SYMBOL_SIZE } from '../game/constants';

	type Props = {
		width: number;
		amount: number;
		animate: boolean;
		oncomplete: () => void;
	};

	// The running cascade total on its iron plaque (TumbleWinAmountFrame). Drawn in code -
	// it used to ride the sample game's tumble_win spine. 'explosion' (a cascade's win
	// added): the number punches up, counts to the new total under a brass flash and
	// settles; 'idle': it just counts. oncomplete fires once the count has landed.
	const props: Props = $props();
	const amount = new Tween(0, { duration: 420, easing: cubicOut });
	const punch = new Tween(1, { duration: 360, easing: backOut });
	const flash = new Tween(0, { duration: 500, easing: cubicOut });

	$effect(() => {
		const target = props.amount;
		if (props.animate) {
			punch.set(1.35, { duration: 0 });
			flash.set(1, { duration: 0 });
			punch.set(1);
			flash.set(0);
			amount.set(target).then(() => props.oncomplete());
		} else {
			amount.set(target).then(() => props.oncomplete());
		}
	});

	const text = $derived(bookEventAmountToCurrencyString(amount.current));
</script>

<Container scale={punch.current}>
	<WinAmountText anchor={0.5} style={{ fontSize: SYMBOL_SIZE * 0.6 }} {text} maxWidth={props.width} />
	{#if flash.current > 0.01}
		<Container alpha={flash.current * 0.8} blendMode="add">
			<WinAmountText anchor={0.5} style={{ fontSize: SYMBOL_SIZE * 0.6 }} {text} maxWidth={props.width} />
		</Container>
	{/if}
</Container>

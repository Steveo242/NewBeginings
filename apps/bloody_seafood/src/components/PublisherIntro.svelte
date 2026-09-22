<script lang="ts">
	import { fade } from 'svelte/transition';

	type Props = { src: string; oncomplete?: () => void };

	const props: Props = $props();

	/** Nothing may hold the game behind the splash if the video stalls or the
	 *  codec is unsupported, so every path out of here funnels through this. */
	let visible = $state(true);
	let video = $state<HTMLVideoElement>();

	const finish = () => {
		if (!visible) return;
		visible = false;
		props.oncomplete?.();
	};

	$effect(() => {
		const el = video;
		if (!el) return;

		// Try with sound first. Browsers only allow unmuted autoplay once the
		// page has been interacted with; where they refuse, play() rejects and
		// we retry muted so the intro still runs rather than sitting frozen on
		// a black screen.
		el.play().catch(() => {
			el.muted = true;
			el.play().catch(finish);
		});

		// Backstop: `ended` never fires if the video never starts.
		const bail = setTimeout(finish, 8000);
		return () => clearTimeout(bail);
	});
</script>

{#if visible}
	<div class="publisher-intro" transition:fade={{ duration: 260 }}>
		<!-- svelte-ignore a11y_media_has_caption -->
		<video
			bind:this={video}
			src={props.src}
			preload="auto"
			playsinline
			onended={finish}
			onerror={finish}
		></video>
	</div>
{/if}

<style lang="scss">
	.publisher-intro {
		position: absolute;
		top: 0;
		left: 0;
		width: 100%;
		height: 100%;
		z-index: 999;
		background-color: #000000;
		display: flex;
		justify-content: center;
		align-items: center;
		overflow: hidden;
	}

	video {
		width: 100%;
		height: 100%;
		object-fit: contain;
	}
</style>

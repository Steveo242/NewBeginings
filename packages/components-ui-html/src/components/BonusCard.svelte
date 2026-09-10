<script lang="ts">
	import type { Snippet } from 'svelte';

	type Props = {
		title: Snippet;
		description: Snippet;
		price: Snippet;
		button: Snippet;
	};

	const props: Props = $props();
</script>

<div class="bonus-card-wrap">
	<div class="info">
		{@render props.title()}
		{@render props.description()}
		{@render props.price()}
	</div>
	{@render props.button()}
</div>

<style lang="scss">
	.bonus-card-wrap {
		padding: 0.5rem;
		flex-direction: column;
		display: flex;
		justify-content: space-between;

		border-radius: 10px;
		background: rgba(0, 0, 0, 0.5);

		border: 8px solid transparent;
		border-image-source: repeating-linear-gradient(
			45deg,
			#8a6a2f 0px,
			#d9b45c 3px,
			#f2dd9a 5px,
			#d9b45c 7px,
			#8a6a2f 10px
		);
		border-image-slice: 8;
		border-image-repeat: repeat;
		text-align: left;
		min-width: 155px;
		max-width: 180px;
		gap: 0.5rem;
	}

	.info {
		display: flex;
		flex-direction: column;
		gap: 0.5em;
	}
</style>

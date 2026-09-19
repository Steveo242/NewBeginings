<script lang="ts">
	// Same runtime-resolved URL pattern game/assets.ts uses for Pixi assets -
	// these are DOM <img> tags, so they can't read frames out of the
	// symbolsStatic atlas and need standalone files. Regenerate them with
	// bs-render/build_paytable_icons.py whenever the symbol art changes.
	const icon = (name: string) =>
		new URL(`../../assets/sprites/paytable/${name}.png`, import.meta.url).href;

	const rows = [
		{ name: 'h1', alt: 'Shark', pays: ['5.00', '12.50', '25.00', '60.00'] },
		{ name: 'h2', alt: 'Angelfish', pays: ['2.00', '5.00', '10.00', '40.00'] },
		{ name: 'h3', alt: 'Clownfish', pays: ['1.30', '3.20', '7.00', '30.00'] },
		{ name: 'h4', alt: 'Grouper', pays: ['1.00', '2.50', '6.00', '20.00'] },
		{ name: 'l1', alt: 'Chum bucket', pays: ['0.60', '1.50', '4.00', '10.00'] },
		{ name: 'l2', alt: 'Chum tub', pays: ['0.40', '1.20', '3.50', '8.00'] },
		{ name: 'l3', alt: 'Chum crate', pays: ['0.20', '0.80', '2.50', '5.00'] },
	];
</script>

<div class="bs-panel">
	<h1 class="bs-title">Paytable</h1>

	<p>
		Values are multiplied by your total play. Clusters of
		<span class="bs-num">5</span> or more matching symbols win.
	</p>

	<table class="bs-table">
		<caption>Cluster size &rarr; win multiplier</caption>
		<thead>
			<tr>
				<th>Symbol</th><th>5</th><th>6&ndash;8</th><th>9&ndash;12</th>
				<th>13+</th>
			</tr>
		</thead>
		<tbody>
			{#each rows as row (row.name)}
				<tr>
					<th><img class="bs-symbol" src={icon(row.name)} alt={row.alt} /></th>
					{#each row.pays as pay}<td>{pay}</td>{/each}
				</tr>
			{/each}
		</tbody>
	</table>

	<h2 class="bs-h2">Special symbols</h2>
	<ul class="bs-specials">
		<li>
			<img class="bs-symbol bs-symbol--special" src={icon('w')} alt="Wild anchor" />
			<span>
				<strong>WILD</strong> &mdash; substitutes for any paying symbol. Appears
				during free spins only. Has no win of its own.
			</span>
		</li>
		<li>
			<img class="bs-symbol bs-symbol--special" src={icon('s')} alt="Scatter chest" />
			<span>
				<strong>SCATTER</strong> &mdash; <span class="bs-num">3</span> or more
				anywhere on the board award free spins. Has no cluster win of its own.
			</span>
		</li>
	</ul>

	<div class="bs-note">
		Theoretical RTP <span class="bs-num">96.70%</span> &middot; maximum win
		<span class="bs-num bs-num--blood">10,000&times;</span> play.
	</div>
</div>

<style lang="scss">

	.bs-panel {
		--plank-dark: #3a2415;
		--plank-mid: #5b3a22;
		--plank-light: #7a5232;
		--brass: #c8a24a;
		--blood: #a4161a;
		--bone: #f2e8d5;

		color: var(--bone);
		font-family: 'Trebuchet MS', 'Segoe UI', system-ui, sans-serif;
		padding: 1.25rem;
		border: 0.4rem solid var(--plank-dark);
		border-radius: 0.4rem;
		box-shadow:
			inset 0 0 0 0.18rem var(--brass),
			inset 0 0 3rem rgba(0, 0, 0, 0.55),
			0 0.5rem 1.5rem rgba(0, 0, 0, 0.6);
		background-color: var(--plank-mid);
		background-image:
			repeating-linear-gradient(
				90deg,
				rgba(0, 0, 0, 0.28) 0 0.12rem,
				rgba(0, 0, 0, 0) 0.12rem 7.5rem
			),
			repeating-linear-gradient(
				0deg,
				rgba(255, 255, 255, 0.035) 0 0.08rem,
				rgba(0, 0, 0, 0.07) 0.08rem 0.5rem
			),
			linear-gradient(180deg, var(--plank-light), var(--plank-dark));
	}

	.bs-title {
		margin: 0 0 1rem;
		text-align: center;
		font-size: 1.9rem;
		font-weight: 900;
		letter-spacing: 0.06em;
		text-transform: uppercase;
		color: var(--bone);
		-webkit-text-stroke: 0.09rem var(--plank-dark);
		text-shadow:
			0 0.14rem 0 var(--plank-dark),
			0 0 0.9rem rgba(200, 162, 74, 0.45);
	}

	.bs-h2 {
		margin: 1.4rem 0 0.5rem;
		font-size: 1.15rem;
		font-weight: 800;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--brass);
		border-bottom: 0.14rem solid rgba(200, 162, 74, 0.4);
		padding-bottom: 0.3rem;
	}

	.bs-panel p,
	.bs-panel li {
		font-size: 1rem;
		line-height: 1.55;
		margin: 0.4rem 0;
	}

	.bs-panel ul {
		margin: 0.4rem 0;
		padding-left: 1.2rem;
	}

	/* oversized bubble numerals for every figure that matters */
	.bs-num {
		display: inline-block;
		padding: 0.05em 0.45em;
		margin: 0 0.12em;
		border-radius: 999px;
		background: linear-gradient(180deg, #fff6df, var(--brass));
		color: #2a1a0d;
		font-weight: 900;
		font-size: 1.12em;
		border: 0.11rem solid var(--plank-dark);
		box-shadow:
			inset 0 0.1rem 0 rgba(255, 255, 255, 0.7),
			0 0.12rem 0 var(--plank-dark);
	}

	.bs-num--blood {
		background: linear-gradient(180deg, #e0575b, var(--blood));
		color: var(--bone);
	}

	.bs-table {
		width: 100%;
		border-collapse: collapse;
		margin-top: 0.5rem;
		background: rgba(0, 0, 0, 0.34);
		border: 0.16rem solid var(--plank-dark);
	}

	.bs-table caption {
		caption-side: top;
		padding-bottom: 0.4rem;
		font-size: 0.9rem;
		color: var(--brass);
	}

	.bs-table th,
	.bs-table td {
		padding: 0.4rem 0.5rem;
		text-align: center;
		border: 0.07rem solid rgba(0, 0, 0, 0.5);
		font-variant-numeric: tabular-nums;
	}

	.bs-table thead th {
		background: rgba(0, 0, 0, 0.45);
		color: var(--brass);
		font-size: 0.9rem;
		text-transform: uppercase;
		letter-spacing: 0.04em;
	}

	.bs-table tbody th {
		background: rgba(0, 0, 0, 0.28);
		color: var(--bone);
		font-weight: 800;
		padding: 0.25rem;
	}

	.bs-symbol {
		display: block;
		width: 2.6rem;
		height: 2.6rem;
		margin: 0 auto;
		object-fit: contain;
		filter: drop-shadow(0 0.1rem 0.15rem rgba(0, 0, 0, 0.6));
	}

	.bs-specials {
		list-style: none;
		padding-left: 0;
	}

	.bs-specials li {
		display: flex;
		align-items: center;
		gap: 0.7rem;
	}

	.bs-symbol--special {
		flex: 0 0 auto;
		width: 3.1rem;
		height: 3.1rem;
		margin: 0;
	}

	.bs-note {
		margin-top: 1.2rem;
		padding: 0.7rem 0.9rem;
		border-left: 0.28rem solid var(--blood);
		background: rgba(0, 0, 0, 0.32);
		font-size: 0.92rem;
		line-height: 1.5;
	}

</style>

<script lang="ts">
</script>

<div class="bs-panel">
	<h1 class="bs-title">Bloody Seafood</h1>

	<p>
		Bloody Seafood is a <span class="bs-num">7</span>&times;<span
			class="bs-num">7</span
		> cluster-wins slot. Symbols do not win on lines &mdash; they win in
		clusters.
	</p>

	<h2 class="bs-h2">How to win</h2>
	<ul>
		<li>
			A win needs <span class="bs-num">5</span> or more matching symbols
			touching each other horizontally or vertically.
		</li>
		<li>
			Winning symbols are removed. Everything above them falls down and new
			symbols drop in to fill the gaps.
		</li>
		<li>
			If the new symbols form another cluster, it wins too. This repeats until
			no new clusters form.
		</li>
		<li>All wins from a single spin are added together.</li>
	</ul>

	<h2 class="bs-h2">Wild</h2>
	<p>
		The <strong>WILD</strong> substitutes for any paying symbol to help complete
		a cluster. It appears only during free spins.
	</p>

	<h2 class="bs-h2">Scatter &amp; free spins</h2>
	<p>
		Landing <span class="bs-num">3</span> or more
		<strong>SCATTER</strong> symbols anywhere on the board awards free spins:
	</p>
	<table class="bs-table">
		<thead>
			<tr><th>Scatters</th><th>Free spins</th></tr>
		</thead>
		<tbody>
			<tr><th>3</th><td>8</td></tr>
			<tr><th>4</th><td>10</td></tr>
			<tr><th>5</th><td>12</td></tr>
			<tr><th>6</th><td>15</td></tr>
			<tr><th>7</th><td>18</td></tr>
		</tbody>
	</table>

	<h2 class="bs-h2">Re-trigger</h2>
	<p>
		Landing <span class="bs-num">3</span> or more scatters during free spins adds
		more spins:
	</p>
	<table class="bs-table">
		<thead>
			<tr><th>Scatters</th><th>Extra spins</th></tr>
		</thead>
		<tbody>
			<tr><th>3</th><td>+5</td></tr>
			<tr><th>4</th><td>+8</td></tr>
			<tr><th>5</th><td>+10</td></tr>
		</tbody>
	</table>

	<h2 class="bs-h2">Global multiplier</h2>
	<p>
		During free spins a global multiplier applies to every cluster win. It
		starts at <span class="bs-num">1&times;</span> when the feature begins,
		climbs as the feature plays out, and its current value is shown beside the
		board. There is no multiplier in the base game.
	</p>

	<h2 class="bs-h2">Play modes</h2>
	<table class="bs-table">
		<thead>
			<tr><th>Mode</th><th>Cost</th><th>What it does</th></tr>
		</thead>
		<tbody>
			<tr>
				<th>Base</th><td>1&times;</td>
				<td>Standard play</td>
			</tr>
			<tr>
				<th>Ante Bonus</th><td>1.5&times;</td>
				<td>Improved chance of triggering free spins</td>
			</tr>
			<tr>
				<th>Ante Super</th><td>2&times;</td>
				<td>Improved chance of triggering the super bonus</td>
			</tr>
			<tr>
				<th>Play Bonus</th><td>100&times;</td>
				<td>Starts free spins immediately from 3 or more scatters</td>
			</tr>
			<tr>
				<th>Play Super</th><td>500&times;</td>
				<td>Starts free spins immediately from 5 or more scatters</td>
			</tr>
		</tbody>
	</table>

	<h2 class="bs-h2">Return to player &amp; max win</h2>
	<p>
		Theoretical RTP is <span class="bs-num">96.70%</span>. Maximum win is
		<span class="bs-num bs-num--blood">10,000&times;</span> your play. A round
		ends immediately once the maximum win is reached.
	</p>

	<h2 class="bs-h2">Playing the game</h2>
	<ul>
		<li>Press the play button, or the space bar, to spin.</li>
		<li>Use the play menu to change your play amount or switch play mode.</li>
		<li>Play Bonus and Play Super ask you to confirm before the play is placed.</li>
		<li>Auto play repeats your current play; you can stop it at any time.</li>
		<li>Sound can be turned off in settings.</li>
	</ul>

	<div class="bs-note">
		Every result is determined the moment you come and play, independently of
		every other play. Nothing you do during a round changes the outcome. Play
		responsibly.

		<p class="bs-disclaimer">
			Malfunction voids all wins and plays. A consistent internet connection is required.
			In the event of a disconnection, reload the game to finish any uncompleted rounds.
			The expected return is calculated over many plays. The game display is not
			representative of any physical device and is for illustrative purposes only.
			Winnings are settled according to the amount received from the Remote Game Server
			and not from events within the web browser. TM and &copy; 2026 Engine.
		</p>
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
	}

	.bs-disclaimer {
		margin-top: 0.9rem;
		font-size: 0.82rem;
		opacity: 0.85;
		line-height: 1.45;
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

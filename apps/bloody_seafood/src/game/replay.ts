import { stateBet, stateBetDerived, stateUi } from 'state-shared';

// Replay links (?replay=true) load one finished round from the RGS into betToResume and
// play it through the resume flow. The resume flow clears betToResume as it starts, so a
// copy is kept here to let the player watch the same round again.
let stashed: string | null = null;

export const isReplay = () => stateUi.config.mode === 'replay';

export const stashReplayRound = () => {
	if (isReplay() && stateBet.betToResume) stashed = JSON.stringify(stateBet.betToResume);
};

export const restoreReplayRound = () => {
	if (!stashed) return false;
	stateBet.betToResume = JSON.parse(stashed);
	return true;
};

/** The mode's full cost multiplier - buy modes included, unlike stateBetDerived.betCost(). */
export const replayCostMultiplier = () => stateBetDerived.activeBetMode()?.costMultiplier ?? 1;

export const replayCost = () => stateBet.betAmount * replayCostMultiplier();

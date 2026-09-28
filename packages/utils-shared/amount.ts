import { stateI18n } from 'state-shared';

import { BOOK_AMOUNT_MULTIPLIER } from 'constants-shared/bet';
import { stateBet } from 'state-shared';

const NO_LOCALISATION_CURRENCY_MAP: Record<string, string> = {
	XGC: 'GC',
	XSC: 'SC',
	// the bare codes too: Intl rejects them as currencies and would throw
	GC: 'GC',
	SC: 'SC',
};

// bookEventAmount: is the amount or win numbers in the events of books, e.g. the amount in setTotalWin bookEvent
// {
// 	"index": 3,
// 	"type": "setTotalWin",
// 	"amount": 100
// },
// if betting on $1,   100 bookEventAmount equals to $1.    betAmountMultiplier is (100 / BOOK_AMOUNT_MULTIPLIER =) 1
// if betting on $1,    50 bookEventAmount equals to $0.5.  betAmountMultiplier is ( 50 / BOOK_AMOUNT_MULTIPLIER =) 0.5
// if betting on $0.5, 100 bookEventAmount equals to $0.5.  betAmountMultiplier is (100 / BOOK_AMOUNT_MULTIPLIER =) 1
// if betting on $0.5,  50 bookEventAmount equals to $0.25. betAmountMultiplier is ( 50 / BOOK_AMOUNT_MULTIPLIER =) 0.5

export const bookEventAmountToBetAmountMultiplier = (bookEventAmount: number) =>
	bookEventAmount / BOOK_AMOUNT_MULTIPLIER;

export const bookEventAmountToNormalisedAmount = (bookEventAmount: number) => {
	const betAmountMultiplier = bookEventAmountToBetAmountMultiplier(bookEventAmount);
	return stateBet.wageredBetAmount * betAmountMultiplier;
};

export const numberToFloat = (value: number) => Number.parseFloat(`${value}`);

// Sub-cent amounts (e.g. a 0.1x win on a small play) would round to 0.00, so they keep
// up to 4 decimals; anything from one cent up stays at 2.
const fractionDigits = (value: number) => (value !== 0 && Math.abs(value) < 0.01 ? 4 : 2);

export const numberToCurrencyString = (value: number) => {
	const maximumFractionDigits = fractionDigits(value);

	if (stateBet.currency in NO_LOCALISATION_CURRENCY_MAP) {
		const fixed = numberToFloat(value).toFixed(maximumFractionDigits);
		const trimmed = maximumFractionDigits > 2 ? fixed.replace(/0{1,2}$/, '') : fixed;
		return `${NO_LOCALISATION_CURRENCY_MAP[stateBet.currency]} ${trimmed}`;
	}

	return stateI18n.i18n.number(value, {
		minimumFractionDigits: 2,
		maximumFractionDigits,
		style: 'currency',
		currency: stateBet.currency,
		// numberingSystem: 'latn',
	});
};

export const bookEventAmountToCurrencyString = (bookEventAmount: number) => {
	const normalisedAmount = bookEventAmountToNormalisedAmount(bookEventAmount);
	return numberToCurrencyString(normalisedAmount);
};

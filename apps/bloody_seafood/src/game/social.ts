import { stateI18nDerived, stateUrlDerived } from 'state-shared';

// Stake.us social mode (social=true): no gambling terms anywhere a player can read them.
// The swaps are Stake Engine's restricted-phrase table (Approval guidelines ->
// Jurisdiction requirements), longest phrase first so "buy bonus" wins over "buy".
// Applied to every translated string (the shared SDK menus, dialogs and messages), to the
// bet-mode texts, and to all HTML text (rules, paytable, menus, the replay window) by a
// MutationObserver, so text added later is caught too.
const SWAPS: [string, string][] = [
	['place your bets', 'come and play'],
	['be awarded to player’s accounts', 'appear in player’s accounts'],
	["be awarded to player's accounts", "appear in player's accounts"],
	['at the cost of', 'for'],
	['cost of', 'can be played for'],
	['bonus buy', 'bonus'],
	['buy bonus', 'get bonus'],
	['total bet', 'total play'],
	['win feature', 'play feature'],
	['paid out', 'win'],
	['pays out', 'won'],
	['pay out', 'win'],
	['paytable', 'win table'],
	['pay table', 'win table'],
	['betting', 'playing'],
	['bets', 'plays'],
	['bet', 'play'],
	['bought', 'instantly triggered'],
	['buy', 'play'],
	['purchase', 'play'],
	['cash', 'coins'],
	['credits', 'balance'],
	['credit', 'balance'],
	['currency', 'token'],
	['deposit', 'get coins'],
	['funds', 'balance'],
	['fund', 'balance'],
	['gamble', 'play'],
	['money', 'coins'],
	['paid', 'won'],
	['payer', 'winner'],
	['pays', 'wins'],
	['pay', 'win'],
	['rebet', 'respin'],
	['stake', 'play amount'],
	['wager', 'play'],
	['withdraw', 'redeem'],
];

const RE = new RegExp(`\\b(${SWAPS.map(([p]) => p.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')).join('|')})\\b`, 'gi');
const TO = new Map(SWAPS.map(([p, r]) => [p.toLowerCase(), r]));

/** the replacement in the matched word's case: BET -> PLAY, Bet -> Play, bet -> play */
const cased = (match: string, rep: string) =>
	match === match.toUpperCase() && match !== match.toLowerCase()
		? rep.toUpperCase()
		: match[0] === match[0].toUpperCase()
			? rep[0].toUpperCase() + rep.slice(1)
			: rep;

export const socialText = (text: string) =>
	stateUrlDerived.social() ? text.replace(RE, (m) => cased(m, TO.get(m.toLowerCase()) ?? m)) : text;

const ATTRS = ['title', 'aria-label', 'alt', 'placeholder'];

const scrub = (node: Node) => {
	if (node.nodeType === Node.TEXT_NODE) {
		const t = node.nodeValue ?? '';
		const s = socialText(t);
		if (s !== t) node.nodeValue = s;
		return;
	}
	if (node.nodeType !== Node.ELEMENT_NODE) return;
	const el = node as Element;
	if (el.tagName === 'SCRIPT' || el.tagName === 'STYLE') return;
	for (const a of ATTRS) {
		const v = el.getAttribute(a);
		if (v) {
			const s = socialText(v);
			if (s !== v) el.setAttribute(a, s);
		}
	}
	el.childNodes.forEach(scrub);
};

let installed = false;

export const installSocialMode = () => {
	if (installed || !stateUrlDerived.social()) return;
	installed = true;
	const translate = stateI18nDerived.translate;
	stateI18nDerived.translate = (value: string) => socialText(translate(value));
	if (typeof document === 'undefined') return;
	scrub(document.body);
	new MutationObserver((records) => {
		for (const r of records) {
			if (r.type === 'characterData') scrub(r.target);
			else if (r.type === 'attributes') scrub(r.target);
			else r.addedNodes.forEach(scrub);
		}
	}).observe(document.body, {
		subtree: true,
		childList: true,
		characterData: true,
		attributes: true,
		attributeFilter: ATTRS,
	});
};

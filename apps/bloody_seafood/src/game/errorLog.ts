// A persistent error log for the problems a player only sees once and can't reproduce
// ("a window popped up"). The last MAX entries - uncaught errors, unhandled rejections,
// console errors (the SDK logs every RGS / auth failure there before its "Sorry, something
// went wrong" modal), render-guard recoveries and load stalls - are kept in localStorage
// across reloads, tagged with the time and the page load they came from. Nothing changes on screen in normal
// play: the log is shown only with ?diag=1 (on load), Ctrl+Shift+D or five quick taps in the
// top-left corner (toggle, any time).
const KEY = 'bs_errlog';
const MAX = 30;

type Entry = { t: string; kind: string; msg: string };

const read = (): Entry[] => {
	try {
		const raw = localStorage.getItem(KEY);
		return raw ? (JSON.parse(raw) as Entry[]) : [];
	} catch {
		return [];
	}
};

const text = (value: unknown): string => {
	// Firefox's stack has no "Name: message" header, so always lead with it
	if (value instanceof Error) return `${value.name}: ${value.message}${value.stack ? '\n' + value.stack.split('\n').slice(0, 4).join('\n') : ''}`;
	if (typeof value === 'string') return value;
	try {
		return JSON.stringify(value);
	} catch {
		return String(value);
	}
};

export const logError = (kind: string, ...parts: unknown[]) => {
	const entry = { t: new Date().toISOString(), kind, msg: parts.map(text).join(' ').slice(0, 600) };
	try {
		localStorage.setItem(KEY, JSON.stringify([...read(), entry].slice(-MAX)));
	} catch {
		// private mode / storage full: the log is best-effort
	}
	if (panel) render();
};

let panel: HTMLDivElement | undefined;
const render = () => {
	if (!panel) return;
	const entries = read();
	panel.querySelector('pre')!.textContent = entries.length
		? entries.map((e) => `${e.t}  [${e.kind}]  ${e.msg}`).join('\n\n')
		: '(no errors logged)';
};
const toggle = () => {
	if (panel) {
		panel.remove();
		panel = undefined;
		return;
	}
	panel = document.createElement('div');
	panel.style.cssText =
		'position:fixed;left:8px;right:8px;top:8px;max-height:70%;overflow:auto;z-index:100000;' +
		'background:rgba(0,0,0,.92);color:#ffd36a;font:12px/1.35 monospace;padding:8px;user-select:text';
	const bar = document.createElement('div');
	bar.style.cssText = 'display:flex;gap:8px;margin-bottom:6px;align-items:center';
	const title = document.createElement('b');
	title.textContent = `ERROR LOG (last ${MAX}, newest last)`;
	title.style.flex = '1';
	const button = (label: string, onclick: () => void) => {
		const b = document.createElement('button');
		b.textContent = label;
		b.style.cssText = 'font:12px monospace;padding:2px 8px';
		b.onclick = onclick;
		return b;
	};
	bar.append(
		title,
		button('copy', () => navigator.clipboard?.writeText(panel?.querySelector('pre')?.textContent ?? '').catch(() => {})),
		button('clear', () => {
			try {
				localStorage.removeItem(KEY);
			} catch {
				// ignore
			}
			render();
		}),
		button('close', toggle),
	);
	const pre = document.createElement('pre');
	pre.style.cssText = 'margin:0;white-space:pre-wrap;word-break:break-word';
	panel.append(bar, pre);
	document.body.appendChild(panel);
	render();
};

if (typeof window !== 'undefined') {
	logError('page', `load ${location.pathname}${location.search.replace(/sessionID=[^&]*/, 'sessionID=…')}`);
	window.addEventListener('error', (e) =>
		logError('error', e.message || e.type, e.filename ? `@ ${e.filename.split('/').pop()}:${e.lineno}` : ''),
	);
	window.addEventListener('unhandledrejection', (e) => logError('rejection', e.reason));
	const error0 = console.error.bind(console);
	console.error = (...args: unknown[]) => {
		logError('console.error', ...args);
		error0(...args);
	};
	// only our own diagnostics: render-guard recoveries, load stalls and load errors
	const warn0 = console.warn.bind(console);
	console.warn = (...args: unknown[]) => {
		const first = String(args[0] ?? '');
		if (first.startsWith('render recovered') || first.startsWith('[diag]')) logError('warn', ...args);
		warn0(...args);
	};
	window.addEventListener('keydown', (e) => {
		if (e.ctrlKey && e.shiftKey && (e.key === 'D' || e.key === 'd')) {
			e.preventDefault();
			toggle();
		}
	});
	// phones have no keyboard: five quick taps in the top-left corner toggle it too
	let taps: number[] = [];
	window.addEventListener(
		'pointerdown',
		(e) => {
			if (e.clientX > 48 || e.clientY > 48) return;
			const now = performance.now();
			taps = [...taps.filter((t) => now - t < 2500), now];
			if (taps.length >= 5) {
				taps = [];
				toggle();
			}
		},
		{ capture: true, passive: true },
	);
	if (new URLSearchParams(location.search).get('diag') === '1') {
		if (document.body) toggle();
		else window.addEventListener('DOMContentLoaded', toggle, { once: true });
	}
}

import { stateMeta } from 'state-shared';

const M = (mode, costMultiplier, type, title, description, dialog, button) => ({
  mode, costMultiplier, type,
  parent: '', children: '',
  assets: { icon: '', dialogImage: '', dialogVolatility: '', volatility: '', button: '' },
  text: {
    title, dialog, description, button,
    betAmountLabel: title,
    tickerIdle: title + ' IS ACTIVE',
    tickerSpin: 'GOOD LUCK',
    bannerText: '',
  },
  maxWin: 10000,
});

export const applyBetModeMeta = () => {
  stateMeta.betModeMeta = {
    base: M('base', 1.0, 'default', '', '', '', ''),
    ante_bonus: M('ante_bonus', 1.5, 'activate',
      'DEEP WATERS',
      'Improved chance of landing the bonus.',
      'Raises the chance of triggering the bonus round. Costs 1.5x the base play amount and stays active until turned off.',
      'ACTIVATE'),
    ante_super: M('ante_super', 2.0, 'activate',
      'BLOOD TIDE',
      'Improved chance of landing the super bonus.',
      'Raises the chance of triggering the super bonus round. Costs 2x the base play amount and stays active until turned off.',
      'ACTIVATE'),
    buy_bonus: M('buy_bonus', 100.0, 'buy',
      'THE HAUL',
      'Start the bonus round immediately.',
      'Begins the bonus round on the next spin for 100x the base play amount.',
      'PLAY'),
    buy_super: M('buy_super', 500.0, 'buy',
      'THE MOTHERLODE',
      'Start the super bonus round immediately.',
      'Begins the super bonus round on the next spin for 500x the base play amount.',
      'PLAY'),
  };
};

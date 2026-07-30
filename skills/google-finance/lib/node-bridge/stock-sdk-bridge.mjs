#!/usr/bin/env node
/**
 * stock-sdk bridge for OpenClaw finance loop.
 *
 * Reads JSON {"tickers":[{"code":"AAPL","market":"us"},...]} from stdin,
 * calls stock-sdk v2 to fetch quotes, normalizes output, prints JSON to stdout.
 *
 * Usage:
 *   echo '{"tickers":[{"code":"AAPL","market":"us"}]}' | node stock-sdk-bridge.mjs
 */
import { StockSDK } from 'stock-sdk';

async function main() {
  const chunks = [];
  for await (const chunk of process.stdin) chunks.push(chunk);
  const input = JSON.parse(Buffer.concat(chunks).toString('utf8'));
  const tickers = input.tickers || [];

  const sdk = new StockSDK();
  const results = [];
  const errors = [];

  // Group by market for batched calls
  const byMarket = { us: [], hk: [], cn: [], fund: [] };
  for (const t of tickers) {
    const m = (t.market || 'us').toLowerCase();
    if (byMarket[m]) {
      byMarket[m].push(t.code);
    } else {
      errors.push({ ticker: t.code, market: m, error: `unsupported market: ${m}` });
    }
  }

  async function fetchMarket(market, codeList, sdkMethod, currencyFallback) {
    if (!codeList.length) return;
    try {
      const quotes = await sdkMethod(codeList);
      for (const q of quotes) {
        results.push(_normalize(q, currencyFallback));
      }
    } catch (e) {
      for (const code of codeList) {
        errors.push({ ticker: code, market, error: e.message });
      }
    }
  }

  await fetchMarket('us', byMarket.us, (codes) => sdk.quotes.us(codes), 'USD');
  await fetchMarket('hk', byMarket.hk, (codes) => sdk.quotes.hk(codes), 'HKD');
  await fetchMarket('cn', byMarket.cn, (codes) => sdk.quotes.cn(codes), 'CNY');
  await fetchMarket('fund', byMarket.fund, (codes) => sdk.quotes.fund(codes), 'CNY');

  console.log(JSON.stringify({
    results,
    errors,
    ts: new Date().toISOString(),
  }, null, 2));
}

/**
 * Normalize stock-sdk Quote shape to the canonical OpenClaw finance schema.
 */
function _normalize(q, fallbackCurrency) {
  let ticker = q.code || '';
  ticker = ticker.split('.')[0];                // "AAPL.OQ" → "AAPL"
  ticker = ticker.replace(/^(sh|sz|hk)/, '');   // "sh600519" → "600519"

  return {
    ticker,
    name: q.name,
    market: q.market || 'US',
    currency: fallbackCurrency,
    price: q.price,
    prev_close: q.prevClose ?? null,
    open: q.open ?? null,
    high: q.high ?? null,
    low: q.low ?? null,
    change: q.change ?? null,
    change_pct: q.changePercent ?? null,
    volume: q.volume ?? null,
    amount: q.amount ?? null,
    turnover_rate: q.turnoverRate ?? null,
    pe: q.pe ?? null,
    pb: q.pb ?? null,
    high_52w: q.high52w ?? null,
    low_52w: q.low52w ?? null,
    source: 'stocksdk',
    source_ts: q.time || null,
    source_tz: q.tz || null,
    raw_source: q.source || null,
  };
}

main().catch(e => {
  console.error(JSON.stringify({ fatal: e.message, stack: e.stack }, null, 2));
  process.exit(1);
});
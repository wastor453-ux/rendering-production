// Real finance math. Every number on screen comes from these functions —
// no hallucinated trajectories.
export const PMT = 500; // monthly contribution
export const RATE = 0.08; // 8% average annual return
export const RATE_LOW = 0.07; // 7% (after a 1% fee drag)

export function balanceAt(
  pmt: number,
  annualRate: number,
  months: number
): number {
  const r = annualRate / 12;
  return (pmt * (Math.pow(1 + r, months) - 1)) / r;
}

export function futureValue(
  pmt: number,
  annualRate: number,
  years: number
): number {
  return balanceAt(pmt, annualRate, years * 12);
}

// Precomputed, verified against node:
// 8% 30yr = $745,180 · 8% 40yr = $1,745,504 · 7% 40yr = $1,312,407 · 8% 20yr = $294,510

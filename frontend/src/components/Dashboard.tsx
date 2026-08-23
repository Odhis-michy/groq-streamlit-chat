"use client";

import { useMemo, useState } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import type { Company } from "@/lib/data";

const STREAMLIT_URL =
  process.env.NEXT_PUBLIC_STREAMLIT_URL ?? "http://localhost:8503";

export default function Dashboard({ companies }: { companies: Company[] }) {
  const sectors = useMemo(
    () => Array.from(new Set(companies.map((c) => c.sector))).sort(),
    [companies]
  );
  const maxPrice = useMemo(
    () => Math.max(...companies.map((c) => c.stakePrice)),
    [companies]
  );

  const [selectedSectors, setSelectedSectors] = useState<string[]>(sectors);
  const [priceCap, setPriceCap] = useState(maxPrice);
  const [minAvgReturn, setMinAvgReturn] = useState(-30);

  const filtered = companies.filter(
    (c) =>
      selectedSectors.includes(c.sector) &&
      c.stakePrice <= priceCap &&
      c.avgReturn >= minAvgReturn
  );

  function toggleSector(sector: string) {
    setSelectedSectors((prev) =>
      prev.includes(sector) ? prev.filter((s) => s !== sector) : [...prev, sector]
    );
  }

  return (
    <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-6 py-10">
      <header>
        <h1 className="text-3xl font-semibold tracking-tight">
          📈 Kenya Investment Explorer
        </h1>
        <p className="mt-1 text-zinc-600 dark:text-zinc-400">
          Browse sample stake prices and returns for NSE-listed Kenyan companies, and ask
          Groq AI about them.
        </p>
        <div className="mt-4 rounded-md border border-amber-300 bg-amber-50 px-4 py-3 text-sm text-amber-900 dark:border-amber-700 dark:bg-amber-950 dark:text-amber-200">
          ⚠️ <strong>Sample/illustrative data only</strong> — figures below are placeholder
          demo data, not live market data, and nothing on this page is financial advice.
        </div>
      </header>

      <div className="grid grid-cols-1 gap-8 lg:grid-cols-[240px_1fr]">
        <aside className="flex flex-col gap-6">
          <div>
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-zinc-500">
              Sector
            </h2>
            <div className="flex flex-col gap-1.5">
              {sectors.map((sector) => (
                <label key={sector} className="flex items-center gap-2 text-sm">
                  <input
                    type="checkbox"
                    checked={selectedSectors.includes(sector)}
                    onChange={() => toggleSector(sector)}
                  />
                  {sector}
                </label>
              ))}
            </div>
          </div>

          <div>
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-zinc-500">
              Max stake price (KES/share)
            </h2>
            <input
              type="range"
              min={0}
              max={maxPrice}
              step={1}
              value={priceCap}
              onChange={(e) => setPriceCap(Number(e.target.value))}
              className="w-full"
            />
            <div className="text-sm text-zinc-500">{priceCap.toFixed(0)}</div>
          </div>

          <div>
            <h2 className="mb-2 text-sm font-semibold uppercase tracking-wide text-zinc-500">
              Min average return (%)
            </h2>
            <input
              type="range"
              min={-30}
              max={30}
              step={0.5}
              value={minAvgReturn}
              onChange={(e) => setMinAvgReturn(Number(e.target.value))}
              className="w-full"
            />
            <div className="text-sm text-zinc-500">{minAvgReturn.toFixed(1)}</div>
          </div>
        </aside>

        <div className="flex flex-col gap-8">
          <section>
            <h2 className="mb-3 text-lg font-medium">
              Investment opportunities ({filtered.length} companies)
            </h2>
            <div className="overflow-x-auto rounded-lg border border-zinc-200 dark:border-zinc-800">
              <table className="w-full min-w-[640px] text-sm">
                <thead className="bg-zinc-100 text-left dark:bg-zinc-900">
                  <tr>
                    <th className="px-3 py-2 font-medium">Company</th>
                    <th className="px-3 py-2 font-medium">Sector</th>
                    <th className="px-3 py-2 text-right font-medium">
                      Stake Price (KES)
                    </th>
                    <th className="px-3 py-2 text-right font-medium">
                      Market Cap (KES Bn)
                    </th>
                    <th className="px-3 py-2 text-right font-medium">Avg Return %</th>
                  </tr>
                </thead>
                <tbody>
                  {filtered.map((c) => (
                    <tr
                      key={c.company}
                      className="border-t border-zinc-200 dark:border-zinc-800"
                    >
                      <td className="px-3 py-2">{c.company}</td>
                      <td className="px-3 py-2 text-zinc-500">{c.sector}</td>
                      <td className="px-3 py-2 text-right">
                        {c.stakePrice.toFixed(2)}
                      </td>
                      <td className="px-3 py-2 text-right">
                        {c.marketCap.toFixed(1)}
                      </td>
                      <td
                        className={`px-3 py-2 text-right font-medium ${
                          c.avgReturn >= 0
                            ? "text-emerald-600 dark:text-emerald-400"
                            : "text-red-600 dark:text-red-400"
                        }`}
                      >
                        {c.avgReturn.toFixed(2)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </section>

          {filtered.length > 0 && (
            <section>
              <h2 className="mb-3 text-lg font-medium">Average return by company</h2>
              <div className="h-80 w-full rounded-lg border border-zinc-200 p-2 dark:border-zinc-800">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={filtered} margin={{ left: 0, right: 12, top: 8, bottom: 40 }}>
                    <CartesianGrid strokeDasharray="3 3" opacity={0.3} />
                    <XAxis
                      dataKey="company"
                      angle={-35}
                      textAnchor="end"
                      interval={0}
                      height={70}
                      tick={{ fontSize: 11 }}
                    />
                    <YAxis tick={{ fontSize: 11 }} />
                    <Tooltip />
                    <Bar dataKey="avgReturn" fill="#2563eb" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </section>
          )}

          <section>
            <h2 className="mb-3 text-lg font-medium">🤖 Ask Groq AI about these opportunities</h2>
            <div className="overflow-hidden rounded-lg border border-zinc-200 dark:border-zinc-800">
              <iframe
                src={STREAMLIT_URL}
                title="Groq AI chat (Streamlit)"
                className="h-[640px] w-full"
              />
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}

import fs from "fs";
import path from "path";

export interface Company {
  company: string;
  sector: string;
  stakePrice: number;
  marketCap: number;
  returns: Record<string, number>;
  avgReturn: number;
}

export interface CompaniesData {
  returnYears: string[];
  companies: Company[];
}

// Single source of truth lives at the repo root (`data/companies.json`) and is shared
// with the Streamlit app (`app.py`) so both surfaces read the same dataset.
const DATA_PATH = path.join(process.cwd(), "..", "data", "companies.json");

export function loadCompanies(): CompaniesData {
  const raw = JSON.parse(fs.readFileSync(DATA_PATH, "utf-8"));
  const companies: Company[] = raw.companies.map((c: Omit<Company, "avgReturn">) => {
    const values: number[] = raw.returnYears.map((y: string) => c.returns[y]);
    const avgReturn = Math.round((values.reduce((a, b) => a + b, 0) / values.length) * 100) / 100;
    return { ...c, avgReturn };
  });
  return { returnYears: raw.returnYears, companies };
}

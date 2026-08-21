import Dashboard from "@/components/Dashboard";
import { loadCompanies } from "@/lib/data";

export default function Home() {
  const { companies } = loadCompanies();
  return (
    <div className="flex flex-1 flex-col bg-zinc-50 dark:bg-black">
      <Dashboard companies={companies} />
    </div>
  );
}

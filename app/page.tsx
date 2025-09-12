
import Image from "next/image";

import fs from "fs";
import path from "path";

async function getCompanies() {
  const companiesDir = path.join(process.cwd(), "companies");
  const companyFiles = fs.readdirSync(companiesDir);
  return companyFiles
    .filter((file) => file.endsWith(".md"))
    .map((mdFile) => {
      const key = mdFile.replace(/\.md$/, "");
      const fileContent = fs.readFileSync(path.join(companiesDir, mdFile), "utf8");
      // Extract company name from markdown (look for '### Name' section)
      let displayName = key;
      const nameMatch = fileContent.match(/### Name\s*([\s\S]*?)(?:###|$)/);
      if (nameMatch && nameMatch[1]) {
        displayName = nameMatch[1].trim().split("\n")[0];
      }
      return {
        key,
        displayName,
      };
    });
}



export default async function Home() {
  const companies = await getCompanies();
  return (
    <div className="font-sans min-h-screen p-8 pb-20">
      <h1 className="text-3xl font-bold mb-8">Fusion Companies</h1>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-8">
        {companies.map((company) => (
          <a
            key={company.key}
            href={`/company/${encodeURIComponent(company.key)}`}
            className="border rounded-lg p-4 flex flex-col items-center hover:shadow-lg transition"
          >
            <span className="text-xl font-semibold mb-2">{company.displayName}</span>
          </a>
        ))}
      </div>
    </div>
  );
}

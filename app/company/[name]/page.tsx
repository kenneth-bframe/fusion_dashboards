
import fs from "fs";
import path from "path";
import matter from "gray-matter";
import Image from "next/image";
import Link from "next/link";
import { notFound } from "next/navigation";
import React from "react";

export async function generateStaticParams() {
  const companiesDir = path.join(process.cwd(), "companies");
  const companyFiles = fs.readdirSync(companiesDir);
  return companyFiles
    .filter((file) => file.endsWith(".md"))
    .map((mdFile) => ({ name: mdFile.replace(/\.md$/, "") }));
}


export default async function CompanyDashboard({ params }: { params: { name: string } }) {
  const companyKey = params.name;
  const companiesDir = path.join(process.cwd(), "companies");
  const mdFile = path.join(companiesDir, `${companyKey}.md`);

  if (!fs.existsSync(mdFile)) {
    notFound();
  }

  const fileContent = fs.readFileSync(mdFile, "utf8");
  const { content } = matter(fileContent);

  // Extract company name from markdown (look for '### Name' section)
  let displayName = companyKey;
  const nameMatch = content.match(/### Name\s*([\s\S]*?)(?:###|$)/);
  if (nameMatch && nameMatch[1]) {
    displayName = nameMatch[1].trim().split("\n")[0];
  }

  // Logo should be in public/companies
  const logoFile = [".png", ".jpg"].map(ext => `${companyKey.toLowerCase().replace(/ /g, "_")}${ext}`)
    .find(filename => fs.existsSync(path.join(process.cwd(), "public/companies", filename)));


  // Parse markdown sections into cards
  const sectionRegex = /### ([^\n]+)\n([\s\S]*?)(?=###|$)/g;
  const cards: { title: string; value: string }[] = [];
  let logoCard: string | null = null;
  let match;
  while ((match = sectionRegex.exec(content)) !== null) {
    const title = match[1].trim();
    const value = match[2].trim();
    const lowerTitle = title.toLowerCase();
    if (lowerTitle === "logo") {
      // Extract logo filename from markdown image syntax
      const logoMatch = value.match(/!\[.*?\]\((.*?)\)/);
      if (logoMatch && logoMatch[1]) {
        logoCard = logoMatch[1];
      }
    } else if (lowerTitle !== "name" && lowerTitle !== "tags") {
      cards.push({ title, value });
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-4 sm:p-8">
  <Link href="/" className="inline-block mb-6 px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition">Home</Link>
      <h1 className="text-3xl font-bold mb-4">{displayName}</h1>
      {logoFile && (
        <Image
          src={`/companies/${logoFile}`}
          alt={`${displayName} logo`}
          width={160}
          height={160}
          className="mb-6 object-contain"
        />
      )}
      <div className="mb-8 flex flex-col gap-4">
        {logoCard && (
          <div className="bg-white rounded-lg shadow p-4 border w-full flex flex-col items-center">
            <Image
              src={`/companies/${logoCard}`}
              alt={`${displayName} logo`}
              width={160}
              height={160}
              className="mb-2 object-contain"
            />
          </div>
        )}
        {cards.map((card) => {
          if (card.title.toLowerCase() === "overview" || card.title.toLowerCase() === "description") {
            return (
              <div key={card.title} className="bg-white rounded-lg shadow p-4 border w-full">
                <div className="font-semibold text-gray-700 mb-2">{card.title}</div>
                <div className="text-gray-900 break-words">{card.value}</div>
              </div>
            );
          }
          return null;
        })}
        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 w-full">
          {cards.map((card) => {
            if (card.title.toLowerCase() !== "overview" && card.title.toLowerCase() !== "description") {
              let valueContent: React.ReactNode = card.value;
              if (card.title.toLowerCase() === "website" && /^https?:\/\//.test(card.value)) {
                valueContent = (
                  <a href={card.value} target="_blank" rel="noopener noreferrer" className="text-blue-600 underline break-all">
                    {card.value}
                  </a>
                );
              }
              if (card.title.toLowerCase() === "location" && card.value) {
                valueContent = card.value;
              }
              return (
                <div key={card.title} className="bg-white rounded-lg shadow p-4 border w-full">
                  <div className="font-semibold text-gray-700 mb-2">{card.title}</div>
                  <div className="text-gray-900 break-words">{valueContent}</div>
                </div>
              );
            }
            return null;
          })}
        </div>
      </div>
      {/* Dashboard charts can be added here using recharts */}
    </div>
  );
}

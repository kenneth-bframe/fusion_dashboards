"use client";

import React from "react";

const themes = [
  "light", "dark", "cupcake", "bumblebee", "emerald", "corporate", "synthwave", "retro", "cyberpunk", "valentine", "halloween", "garden", "forest", "aqua", "lofi", "pastel", "fantasy", "wireframe", "black", "luxury", "dracula"
];

export default function ThemeSelector() {
  return (
    <div className="w-full flex justify-end p-4">
      <select
        className="select select-bordered w-48"
        onChange={e => {
          if (typeof window !== "undefined") {
            document.querySelector('html')?.setAttribute('data-theme', e.target.value);
          }
        }}
        defaultValue="light"
      >
        {themes.map(theme => (
          <option key={theme} value={theme}>{theme.charAt(0).toUpperCase() + theme.slice(1)}</option>
        ))}
      </select>
    </div>
  );
}

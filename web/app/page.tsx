"use client";

import { useEffect, useState, useCallback } from "react";

type Source = {
  id: string;
  name: string;
  url: string;
  active: boolean;
};

type Theme = {
  id: string;
  name: string;
  emoji: string;
  active: boolean;
  keywords_fr: string[];
  keywords_en: string[];
};

type Config = {
  sources: Source[];
  themes: Theme[];
  zones: string[];
  recipients: string[];
};

type SourceStatus = "idle" | "testing" | "ok" | "error";

const ZONES_OPTIONS = [
  { id: "senegal", label: "Sénégal" },
  { id: "afrique_ouest", label: "Afrique de l'Ouest (CEDEAO)" },
  { id: "international", label: "International (PNUD / BM / UE)" },
];

export default function HomePage() {
  const [authed, setAuthed] = useState(false);
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState("");
  const [authLoading, setAuthLoading] = useState(false);

  const [config, setConfig] = useState<Config | null>(null);
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [running, setRunning] = useState(false);
  const [saveMsg, setSaveMsg] = useState("");
  const [runMsg, setRunMsg] = useState("");

  const [sourceStatuses, setSourceStatuses] = useState<Record<string, SourceStatus>>({});
  const [sourceErrors, setSourceErrors] = useState<Record<string, string>>({});

  const [newSource, setNewSource] = useState({ name: "", url: "" });
  const [newRecipient, setNewRecipient] = useState("");
  const [newKeyword, setNewKeyword] = useState({ themeId: "", lang: "fr", value: "" });

  const loadConfig = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/get-config");
      if (!res.ok) throw new Error("Erreur chargement config");
      const data = await res.json();
      setConfig(data);
    } catch {
      setConfig(null);
    } finally {
      setLoading(false);
    }
  }, []);

  async function handleAuth(e: React.FormEvent) {
    e.preventDefault();
    setAuthLoading(true);
    setAuthError("");
    try {
      const res = await fetch("/api/auth", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ password }),
      });
      if (res.ok) {
        setAuthed(true);
        loadConfig();
      } else {
        setAuthError("Mot de passe incorrect");
      }
    } catch {
      setAuthError("Erreur de connexion");
    } finally {
      setAuthLoading(false);
    }
  }

  async function handleSave() {
    if (!config) return;
    setSaving(true);
    setSaveMsg("");
    try {
      const res = await fetch("/api/save-config", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(config),
      });
      const data = await res.json();
      setSaveMsg(res.ok ? "✅ Sauvegardé sur GitHub" : `❌ ${data.error}`);
    } catch {
      setSaveMsg("❌ Erreur réseau");
    } finally {
      setSaving(false);
      setTimeout(() => setSaveMsg(""), 4000);
    }
  }

  async function handleRunScraper() {
    setRunning(true);
    setRunMsg("");
    try {
      const res = await fetch("/api/run-scraper", { method: "POST" });
      const data = await res.json();
      setRunMsg(res.ok ? "✅ Scraper lancé (GitHub Actions)" : `❌ ${data.error}`);
    } catch {
      setRunMsg("❌ Erreur réseau");
    } finally {
      setRunning(false);
      setTimeout(() => setRunMsg(""), 6000);
    }
  }

  async function testSource(source: Source) {
    setSourceStatuses((s) => ({ ...s, [source.id]: "testing" }));
    setSourceErrors((e) => ({ ...e, [source.id]: "" }));
    try {
      const res = await fetch("/api/test-source", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: source.url }),
      });
      const data = await res.json();
      if (res.ok && data.ok) {
        setSourceStatuses((s) => ({ ...s, [source.id]: "ok" }));
      } else {
        setSourceStatuses((s) => ({ ...s, [source.id]: "error" }));
        setSourceErrors((e) => ({ ...e, [source.id]: data.error || "Inaccessible" }));
      }
    } catch {
      setSourceStatuses((s) => ({ ...s, [source.id]: "error" }));
      setSourceErrors((e) => ({ ...e, [source.id]: "Erreur réseau" }));
    }
  }

  function toggleSource(id: string) {
    setConfig((c) =>
      c ? { ...c, sources: c.sources.map((s) => s.id === id ? { ...s, active: !s.active } : s) } : c
    );
  }

  function removeSource(id: string) {
    setConfig((c) => c ? { ...c, sources: c.sources.filter((s) => s.id !== id) } : c);
  }

  function addSource() {
    if (!newSource.name.trim() || !newSource.url.trim()) return;
    const id = newSource.name.toLowerCase().replace(/[^a-z0-9]/g, "_");
    setConfig((c) =>
      c ? { ...c, sources: [...c.sources, { id, ...newSource, active: true }] } : c
    );
    setNewSource({ name: "", url: "" });
  }

  function toggleTheme(id: string) {
    setConfig((c) =>
      c ? { ...c, themes: c.themes.map((t) => t.id === id ? { ...t, active: !t.active } : t) } : c
    );
  }

  function toggleZone(zone: string) {
    setConfig((c) => {
      if (!c) return c;
      const zones = c.zones.includes(zone)
        ? c.zones.filter((z) => z !== zone)
        : [...c.zones, zone];
      return { ...c, zones };
    });
  }

  function addRecipient() {
    if (!newRecipient.trim() || !newRecipient.includes("@")) return;
    setConfig((c) =>
      c && !c.recipients.includes(newRecipient)
        ? { ...c, recipients: [...c.recipients, newRecipient.trim()] }
        : c
    );
    setNewRecipient("");
  }

  function removeRecipient(email: string) {
    setConfig((c) => c ? { ...c, recipients: c.recipients.filter((r) => r !== email) } : c);
  }

  function addKeyword() {
    if (!newKeyword.themeId || !newKeyword.value.trim()) return;
    setConfig((c) => {
      if (!c) return c;
      return {
        ...c,
        themes: c.themes.map((t) => {
          if (t.id !== newKeyword.themeId) return t;
          const field = newKeyword.lang === "fr" ? "keywords_fr" : "keywords_en";
          if (t[field].includes(newKeyword.value.trim())) return t;
          return { ...t, [field]: [...t[field], newKeyword.value.trim()] };
        }),
      };
    });
    setNewKeyword((k) => ({ ...k, value: "" }));
  }

  function removeKeyword(themeId: string, lang: "fr" | "en", kw: string) {
    setConfig((c) => {
      if (!c) return c;
      return {
        ...c,
        themes: c.themes.map((t) => {
          if (t.id !== themeId) return t;
          const field = lang === "fr" ? "keywords_fr" : "keywords_en";
          return { ...t, [field]: t[field].filter((k) => k !== kw) };
        }),
      };
    });
  }

  if (!authed) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <div className="bg-gray-900 border border-gray-800 rounded-2xl p-8 w-full max-w-sm shadow-2xl">
          <div className="text-center mb-6">
            <div className="text-4xl mb-2">🔍</div>
            <h1 className="text-xl font-bold text-white">Veille AO</h1>
            <p className="text-gray-400 text-sm mt-1">Configuration admin</p>
          </div>
          <form onSubmit={handleAuth} className="space-y-4">
            <input
              type="password"
              placeholder="Mot de passe admin"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-4 py-3 text-white placeholder-gray-500 focus:outline-none focus:border-blue-500"
              autoFocus
            />
            {authError && <p className="text-red-400 text-sm">{authError}</p>}
            <button
              type="submit"
              disabled={authLoading}
              className="w-full bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white font-semibold py-3 rounded-lg transition-colors"
            >
              {authLoading ? "Connexion..." : "Entrer"}
            </button>
          </form>
        </div>
      </div>
    );
  }

  if (loading || !config) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-950">
        <div className="text-gray-400 text-lg">Chargement de la configuration...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="bg-gray-900 border-b border-gray-800 sticky top-0 z-10">
        <div className="max-w-4xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="text-2xl">🔍</span>
            <div>
              <h1 className="text-lg font-bold text-white">Veille AO</h1>
              <p className="text-gray-400 text-xs">Configuration scraper</p>
            </div>
          </div>
          <div className="flex items-center gap-3">
            {saveMsg && <span className="text-sm">{saveMsg}</span>}
            {runMsg && <span className="text-sm">{runMsg}</span>}
            <button
              onClick={handleSave}
              disabled={saving}
              className="bg-gray-700 hover:bg-gray-600 disabled:opacity-50 text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
            >
              {saving ? "Sauvegarde..." : "💾 Sauvegarder"}
            </button>
            <button
              onClick={handleRunScraper}
              disabled={running}
              className="bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white text-sm font-semibold px-4 py-2 rounded-lg transition-colors"
            >
              {running ? "Lancement..." : "▶ Lancer le scraper"}
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto px-4 py-8 space-y-8">

        {/* SOURCES */}
        <section>
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            🌐 Sources <span className="text-gray-500 text-sm font-normal">({config.sources.filter(s => s.active).length}/{config.sources.length} actives)</span>
          </h2>
          <div className="space-y-3">
            {config.sources.map((source) => {
              const status = sourceStatuses[source.id] || "idle";
              return (
                <div
                  key={source.id}
                  className={`bg-gray-900 border rounded-xl p-4 flex items-center gap-4 transition-all ${
                    source.active ? "border-gray-700" : "border-gray-800 opacity-60"
                  }`}
                >
                  <button
                    onClick={() => toggleSource(source.id)}
                    className={`relative w-11 h-6 rounded-full transition-colors flex-shrink-0 ${
                      source.active ? "bg-blue-600" : "bg-gray-700"
                    }`}
                    title={source.active ? "Désactiver" : "Activer"}
                  >
                    <span
                      className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                        source.active ? "translate-x-6" : "translate-x-1"
                      }`}
                    />
                  </button>
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold text-white">{source.name}</span>
                      {status === "ok" && <span className="text-green-400 text-xs">✓ Accessible</span>}
                      {status === "error" && (
                        <span className="text-red-400 text-xs">✗ {sourceErrors[source.id]}</span>
                      )}
                    </div>
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-400 text-xs hover:underline truncate block"
                    >
                      {source.url}
                    </a>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <button
                      onClick={() => testSource(source)}
                      disabled={status === "testing"}
                      className="bg-gray-800 hover:bg-gray-700 disabled:opacity-50 text-gray-300 text-xs px-3 py-1.5 rounded-lg transition-colors"
                    >
                      {status === "testing" ? "Test..." : "Tester"}
                    </button>
                    <button
                      onClick={() => removeSource(source.id)}
                      className="text-gray-600 hover:text-red-400 text-lg leading-none transition-colors"
                      title="Supprimer"
                    >
                      ×
                    </button>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Add source form */}
          <div className="mt-4 bg-gray-900 border border-dashed border-gray-700 rounded-xl p-4">
            <p className="text-gray-400 text-sm mb-3">Ajouter une source</p>
            <div className="flex gap-2">
              <input
                type="text"
                placeholder="Nom (ex: ARMP)"
                value={newSource.name}
                onChange={(e) => setNewSource((s) => ({ ...s, name: e.target.value }))}
                className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 w-32"
              />
              <input
                type="url"
                placeholder="https://..."
                value={newSource.url}
                onChange={(e) => setNewSource((s) => ({ ...s, url: e.target.value }))}
                className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 flex-1"
              />
              <button
                onClick={addSource}
                disabled={!newSource.name.trim() || !newSource.url.trim()}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-40 text-white text-sm px-4 py-2 rounded-lg transition-colors"
              >
                + Ajouter
              </button>
            </div>
          </div>
        </section>

        {/* THEMES */}
        <section>
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            🏷️ Thèmes & Mots-clés <span className="text-gray-500 text-sm font-normal">({config.themes.filter(t => t.active).length} actifs)</span>
          </h2>
          <div className="grid gap-4">
            {config.themes.map((theme) => (
              <div
                key={theme.id}
                className={`bg-gray-900 border rounded-xl overflow-hidden transition-all ${
                  theme.active ? "border-gray-700" : "border-gray-800"
                }`}
              >
                <div className="flex items-center gap-3 px-4 py-3">
                  <button
                    onClick={() => toggleTheme(theme.id)}
                    className={`relative w-11 h-6 rounded-full transition-colors flex-shrink-0 ${
                      theme.active ? "bg-blue-600" : "bg-gray-700"
                    }`}
                  >
                    <span
                      className={`absolute top-1 w-4 h-4 bg-white rounded-full shadow transition-transform ${
                        theme.active ? "translate-x-6" : "translate-x-1"
                      }`}
                    />
                  </button>
                  <span className="text-xl">{theme.emoji}</span>
                  <span className={`font-semibold ${theme.active ? "text-white" : "text-gray-500"}`}>
                    {theme.name}
                  </span>
                  <span className="text-gray-600 text-xs ml-auto">
                    {theme.keywords_fr.length + theme.keywords_en.length} mots-clés
                  </span>
                </div>

                {theme.active && (
                  <div className="px-4 pb-4 space-y-3">
                    {/* FR keywords */}
                    <div>
                      <p className="text-gray-500 text-xs mb-2">Français</p>
                      <div className="flex flex-wrap gap-1.5">
                        {theme.keywords_fr.map((kw) => (
                          <span
                            key={kw}
                            className="bg-gray-800 text-gray-300 text-xs px-2 py-1 rounded-md flex items-center gap-1"
                          >
                            {kw}
                            <button
                              onClick={() => removeKeyword(theme.id, "fr", kw)}
                              className="text-gray-600 hover:text-red-400 ml-0.5"
                            >
                              ×
                            </button>
                          </span>
                        ))}
                      </div>
                    </div>
                    {/* EN keywords */}
                    <div>
                      <p className="text-gray-500 text-xs mb-2">English</p>
                      <div className="flex flex-wrap gap-1.5">
                        {theme.keywords_en.map((kw) => (
                          <span
                            key={kw}
                            className="bg-gray-800 text-gray-300 text-xs px-2 py-1 rounded-md flex items-center gap-1"
                          >
                            {kw}
                            <button
                              onClick={() => removeKeyword(theme.id, "en", kw)}
                              className="text-gray-600 hover:text-red-400 ml-0.5"
                            >
                              ×
                            </button>
                          </span>
                        ))}
                      </div>
                    </div>
                    {/* Add keyword */}
                    <div className="flex gap-2 pt-1">
                      <select
                        value={newKeyword.themeId === theme.id ? newKeyword.lang : "fr"}
                        onChange={(e) =>
                          setNewKeyword({ themeId: theme.id, lang: e.target.value, value: "" })
                        }
                        onFocus={() => setNewKeyword((k) => ({ ...k, themeId: theme.id }))}
                        className="bg-gray-800 border border-gray-700 text-gray-300 text-xs rounded-lg px-2 py-1.5 focus:outline-none"
                      >
                        <option value="fr">FR</option>
                        <option value="en">EN</option>
                      </select>
                      <input
                        type="text"
                        placeholder="Nouveau mot-clé..."
                        value={newKeyword.themeId === theme.id ? newKeyword.value : ""}
                        onFocus={() => setNewKeyword((k) => ({ ...k, themeId: theme.id }))}
                        onChange={(e) =>
                          setNewKeyword({ themeId: theme.id, lang: newKeyword.lang, value: e.target.value })
                        }
                        onKeyDown={(e) => {
                          if (e.key === "Enter") addKeyword();
                        }}
                        className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-1.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 flex-1"
                      />
                      <button
                        onClick={addKeyword}
                        className="bg-gray-700 hover:bg-gray-600 text-gray-300 text-xs px-3 py-1.5 rounded-lg transition-colors"
                      >
                        + Ajouter
                      </button>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </section>

        {/* ZONES */}
        <section>
          <h2 className="text-lg font-semibold text-white mb-4">🌍 Zones géographiques</h2>
          <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 space-y-3">
            {ZONES_OPTIONS.map((zone) => (
              <label key={zone.id} className="flex items-center gap-3 cursor-pointer group">
                <div
                  onClick={() => toggleZone(zone.id)}
                  className={`w-5 h-5 rounded border-2 flex items-center justify-center transition-colors cursor-pointer ${
                    config.zones.includes(zone.id)
                      ? "bg-blue-600 border-blue-600"
                      : "border-gray-600 hover:border-gray-400"
                  }`}
                >
                  {config.zones.includes(zone.id) && (
                    <svg className="w-3 h-3 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                    </svg>
                  )}
                </div>
                <span
                  onClick={() => toggleZone(zone.id)}
                  className={`transition-colors ${
                    config.zones.includes(zone.id) ? "text-white" : "text-gray-400 group-hover:text-gray-300"
                  }`}
                >
                  {zone.label}
                </span>
              </label>
            ))}
          </div>
        </section>

        {/* RECIPIENTS */}
        <section>
          <h2 className="text-lg font-semibold text-white mb-4">
            📧 Destinataires <span className="text-gray-500 text-sm font-normal">({config.recipients.length})</span>
          </h2>
          <div className="bg-gray-900 border border-gray-700 rounded-xl p-4 space-y-3">
            {config.recipients.map((email) => (
              <div key={email} className="flex items-center justify-between bg-gray-800 rounded-lg px-3 py-2">
                <span className="text-gray-200 text-sm">{email}</span>
                <button
                  onClick={() => removeRecipient(email)}
                  className="text-gray-600 hover:text-red-400 text-lg leading-none transition-colors"
                >
                  ×
                </button>
              </div>
            ))}
            <div className="flex gap-2 pt-1">
              <input
                type="email"
                placeholder="Ajouter un email..."
                value={newRecipient}
                onChange={(e) => setNewRecipient(e.target.value)}
                onKeyDown={(e) => { if (e.key === "Enter") addRecipient(); }}
                className="bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-blue-500 flex-1"
              />
              <button
                onClick={addRecipient}
                disabled={!newRecipient.includes("@")}
                className="bg-gray-700 hover:bg-gray-600 disabled:opacity-40 text-gray-300 text-sm px-4 py-2 rounded-lg transition-colors"
              >
                + Ajouter
              </button>
            </div>
          </div>
        </section>

        {/* SAVE FOOTER */}
        <div className="pb-8 flex items-center justify-between pt-4 border-t border-gray-800">
          <p className="text-gray-500 text-sm">
            Les modifications sont sauvegardées dans <code className="text-gray-400">config.json</code> sur GitHub.
          </p>
          <div className="flex gap-3">
            <button
              onClick={handleSave}
              disabled={saving}
              className="bg-gray-700 hover:bg-gray-600 disabled:opacity-50 text-white font-medium px-6 py-2.5 rounded-lg transition-colors"
            >
              {saving ? "Sauvegarde..." : "💾 Sauvegarder"}
            </button>
            <button
              onClick={handleRunScraper}
              disabled={running}
              className="bg-green-600 hover:bg-green-700 disabled:opacity-50 text-white font-semibold px-6 py-2.5 rounded-lg transition-colors"
            >
              {running ? "Lancement..." : "▶ Lancer maintenant"}
            </button>
          </div>
        </div>

      </main>
    </div>
  );
}

import { useCallback, useEffect, useState } from "react";

const rawApiUrl = import.meta.env.VITE_API_URL || "/api";
const API_URL = rawApiUrl.replace(/\/+$/, "");
const initialForm = { input_text: "", message_type: "Email", tone: "Formal", language: "English", length: "Medium" };
const options = {
  message_type: ["Email", "Message"],
  tone: ["Formal", "Professional", "Casual", "Friendly", "Polite", "Apologetic", "Urgent"],
  language: ["English", "Tamil", "Hindi"],
  length: ["Short", "Medium", "Detailed"]
};
const toneMeta = {
  Formal: { icon: "\u{1F3A9}", color: "formal" },
  Professional: { icon: "\u{1F4BC}", color: "professional" },
  Casual: { icon: "\u{1F60A}", color: "casual" },
  Friendly: { icon: "\u{1F324}\u{FE0F}", color: "friendly" },
  Polite: { icon: "\u{1F64F}", color: "polite" },
  Apologetic: { icon: "\u{1F647}", color: "apologetic" },
  Urgent: { icon: "\u{26A1}", color: "urgent" }
};

function formatTime(dateStr) {
  if (!dateStr) return "";
  const parts = dateStr.split(" ");
  if (parts.length === 2) {
    const timeParts = parts[1].split(":");
    return `${timeParts[0]}:${timeParts[1]}`;
  }
  return dateStr;
}

async function request(path, init) {
  try {
    const response = await fetch(`${API_URL}${path}`, init);
    const payload = await response.json().catch(() => ({}));
    if (!response.ok || payload.success === false) {
      const errorMsg =
        payload.error ||
        (response.status === 429
          ? "AI rate limit reached. Please wait a moment before trying again."
          : response.status === 503
          ? "AI service is currently busy. Please try again shortly."
          : `Request failed (HTTP ${response.status})`);
      throw new Error(errorMsg);
    }
    return payload;
  } catch (err) {
    if (err.name === "TypeError" && err.message.toLowerCase().includes("fetch")) {
      throw new Error("Unable to connect to the backend server. Please verify the service is running.");
    }
    throw err;
  }
}

export default function App() {
  const [form, setForm] = useState(initialForm);
  const [output, setOutput] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [activeTab, setActiveTab] = useState("generator");
  const [theme, setTheme] = useState("light");
  const [historyTone, setHistoryTone] = useState("All");
  const [historyType, setHistoryType] = useState("All");
  const [mobileHistoryOpen, setMobileHistoryOpen] = useState(false);

  const fetchHistory = useCallback(async (tone = historyTone, type = historyType) => {
    try {
      const params = new URLSearchParams();
      if (tone !== "All") params.set("tone", tone);
      if (type !== "All") params.set("type", type);
      const query = params.toString();
      const result = await request(`/history${query ? `?${query}` : ""}`);
      setHistory(result.data || []);
    } catch (err) {
      setError(`Unable to load history: ${err.message}`);
    }
  }, [historyTone, historyType]);

  useEffect(() => {
    fetchHistory();
  }, [fetchHistory]);

  useEffect(() => {
    if (!notice && !error) return undefined;
    const timeout = window.setTimeout(() => {
      setNotice("");
      setError("");
    }, 3500);
    return () => window.clearTimeout(timeout);
  }, [notice, error]);

  const updateForm = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const generate = async () => {
    if (loading) return; // Prevent duplicate concurrent requests
    if (!form.input_text.trim()) {
      setError("Please enter a message to transform.");
      return;
    }
    setLoading(true);
    setError("");
    setNotice("");
    try {
      const result = await request("/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ ...form, input_text: form.input_text.trim() })
      });
      setOutput(result.data.generated_text);
      setNotice("Message generated successfully.");
      fetchHistory();
    } catch (err) {
      setError(err.message || "Failed to generate message. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  const loadHistoryItem = (item) => {
    setOutput(item.generated_text);
    setForm({
      input_text: item.input_text,
      message_type: item.message_type,
      tone: item.tone,
      language: item.language,
      length: item.length
    });
    setActiveTab("generator");
    if (window.innerWidth < 768) {
      setMobileHistoryOpen(false);
    }
  };

  const deleteItem = async (id) => {
    if (!window.confirm("Delete this history item?")) return;
    try {
      await request(`/history/${id}`, { method: "DELETE" });
      setNotice("History item deleted.");
      fetchHistory();
    } catch (err) {
      setError(err.message);
    }
  };

  const clearHistory = async () => {
    if (!window.confirm("Clear all saved history?")) return;
    try {
      await request("/history", { method: "DELETE" });
      setHistory([]);
      setNotice("History cleared.");
    } catch (err) {
      setError(err.message);
    }
  };

  const copyOutput = async () => {
    try {
      await navigator.clipboard.writeText(output);
      setNotice("Copied to clipboard.");
    } catch {
      setError("Unable to copy the generated message.");
    }
  };

  return (
    <div className="app-shell" data-theme={theme}>
      <aside className={`sidebar ${mobileHistoryOpen ? "sidebar-mobile-open" : ""}`} aria-label="Generation history">
        <div className="sidebar-top-bar">
          <div className="brand">
            <span className="brand-mark">TG</span>
            <div>
              <strong>Tone Generator</strong>
              <small>AI writing assistant</small>
            </div>
          </div>
          <button
            className="mobile-history-toggle"
            onClick={() => setMobileHistoryOpen(!mobileHistoryOpen)}
            aria-label={mobileHistoryOpen ? "Collapse history" : "Expand history"}
          >
            {mobileHistoryOpen ? "✕ Close" : `◷ History (${history.length})`}
          </button>
        </div>

        <div className="sidebar-content-wrapper">
          <div className="sidebar-heading">
            <span>History</span>
            <button className="icon-button" onClick={() => fetchHistory()} title="Refresh history" aria-label="Refresh history">↻</button>
          </div>
          <div className="history-filters">
            <label>
              <span>Tone</span>
              <select value={historyTone} onChange={(event) => setHistoryTone(event.target.value)}>
                <option>All</option>
                {options.tone.map((tone) => <option key={tone}>{tone}</option>)}
              </select>
            </label>
            <label>
              <span>Type</span>
              <select value={historyType} onChange={(event) => setHistoryType(event.target.value)}>
                <option>All</option>
                {options.message_type.map((type) => <option key={type}>{type}</option>)}
              </select>
            </label>
          </div>
          <button className="clear-history" onClick={clearHistory}>Clear history</button>
          <div className="sidebar-history" role="region" aria-label="Recent generations">
            {history.length === 0 ? (
              <div className="sidebar-empty">
                <span>◷</span>
                <p>No generations yet.<br />Your saved messages will appear here.</p>
              </div>
            ) : (
              history.map((item) => (
                <button
                  key={item.id}
                  className={`history-link tone-${toneMeta[item.tone]?.color || "formal"}`}
                  onClick={() => loadHistoryItem(item)}
                  title={`Click to load: "${item.input_text}"`}
                >
                  <div className="history-meta">
                    <span>{item.message_type}</span>
                    <span>{toneMeta[item.tone]?.icon} {item.tone}</span>
                    {item.created_at && <span className="history-time">{formatTime(item.created_at)}</span>}
                  </div>
                  <strong>{item.input_text}</strong>
                </button>
              ))
            )}
          </div>
        </div>
      </aside>

      <main className="page">
        <button
          className="theme-toggle"
          onClick={() => setTheme(theme === "light" ? "dark" : "light")}
          aria-label={`Switch to ${theme === "light" ? "dark" : "light"} theme`}
          title={`Switch to ${theme === "light" ? "dark" : "light"} theme`}
        >
          {theme === "light" ? "☾" : "☀"}
        </button>

        <header className="hero">
          <p className="eyebrow">TONE-BASED WRITING</p>
          <h1>Tone-Based Email &amp; Message Generator</h1>
          <p>Turn a rough thought into a clear, polished message in the tone and language you need.</p>
        </header>

        <div className="tabs" role="tablist">
          <button
            role="tab"
            aria-selected={activeTab === "generator"}
            className={activeTab === "generator" ? "active" : ""}
            onClick={() => setActiveTab("generator")}
          >
            Create message
          </button>
          <button
            role="tab"
            aria-selected={activeTab === "history"}
            className={activeTab === "history" ? "active" : ""}
            onClick={() => setActiveTab("history")}
          >
            Saved history ({history.length})
          </button>
        </div>

        {activeTab === "generator" ? (
          <>
            <section className="input-card">
              <div className="field-heading">
                <label htmlFor="input_text">What would you like to say?</label>
                <span>Start with a rough message—we will refine it.</span>
              </div>
              <textarea
                className={error && !form.input_text.trim() ? "has-error" : ""}
                id="input_text"
                name="input_text"
                value={form.input_text}
                onChange={updateForm}
                placeholder="Example: I need to take leave tomorrow because of a family function."
                rows="7"
                disabled={loading}
              />
              <p className="character-count">{form.input_text.length} / 3000</p>
            </section>

            <section className="settings-card">
              <div className="card-title">
                <h2>Message settings</h2>
                <p>Choose how your message should sound.</p>
              </div>
              <div className="form-grid">
                <Select label="Type" name="message_type" value={form.message_type} onChange={updateForm} values={options.message_type} disabled={loading} />
                <Select label="Tone" name="tone" value={form.tone} onChange={updateForm} values={options.tone} disabled={loading} />
                <Select label="Language" name="language" value={form.language} onChange={updateForm} values={options.language} disabled={loading} />
                <Select label="Length" name="length" value={form.length} onChange={updateForm} values={options.length} disabled={loading} />
              </div>
            </section>

            <div className="actions">
              <button
                className="primary"
                onClick={generate}
                disabled={loading}
                aria-busy={loading}
              >
                {loading ? (
                  <>
                    <span className="spinner" />
                    Generating...
                  </>
                ) : (
                  "Generate"
                )}
              </button>
              <button
                className="secondary"
                onClick={() => {
                  setForm(initialForm);
                  setOutput("");
                  setError("");
                }}
                disabled={loading}
              >
                Clear
              </button>
            </div>

            {loading && (
              <section className="output-card output-loading-card" aria-label="Generating your message" aria-busy="true">
                <div className="loading-status-row">
                  <span className="spinner spinner-primary" />
                  <div>
                    <h3>Generating your message...</h3>
                    <p>Composing a refined {form.tone.toLowerCase()} {form.message_type.toLowerCase()} in {form.language}</p>
                  </div>
                </div>
                <div className="skeleton-line wide" />
                <div className="skeleton-line" />
                <div className="skeleton-line medium" />
                <div className="skeleton-line short" />
              </section>
            )}

            {output && !loading && (
              <section className={`output-card output-ready tone-${toneMeta[form.tone]?.color || "formal"}`}>
                <div className="output-heading">
                  <div>
                    <p className="section-label">GENERATED OUTPUT</p>
                    <h2>Ready to send</h2>
                  </div>
                  <span>{toneMeta[form.tone]?.icon || ""} {form.tone}</span>
                </div>
                <pre>{output}</pre>
                <p className="character-count output-count">{output.length} characters</p>
                <div className="output-footer">
                  <button className="secondary" onClick={copyOutput}>Copy</button>
                  <button className="secondary" onClick={generate} disabled={loading}>Regenerate</button>
                </div>
              </section>
            )}
          </>
        ) : (
          <section className="history-panel">
            <div className="history-title">
              <div>
                <p className="section-label">YOUR SAVED MESSAGES</p>
                <h2>Generation history</h2>
              </div>
              <button className="secondary" onClick={() => fetchHistory()}>Refresh</button>
            </div>
            {history.length === 0 ? (
              <div className="empty-state">
                <span>◷</span>
                <h3>No history yet</h3>
                <p>Generated messages will be saved here for easy access.</p>
              </div>
            ) : (
              history.map((item) => (
                <article className={`history-card tone-${toneMeta[item.tone]?.color || "formal"}`} key={item.id}>
                  <div className="history-card-top">
                    <div className="badges">
                      <span>{item.message_type}</span>
                      <span>{toneMeta[item.tone]?.icon} {item.tone}</span>
                      <span>{item.language}</span>
                      <span>{item.length}</span>
                    </div>
                    <small>{item.created_at}</small>
                  </div>
                  <p><strong>Original:</strong> {item.input_text}</p>
                  <pre>{item.generated_text}</pre>
                  <div className="output-footer">
                    <button className="secondary" onClick={() => loadHistoryItem(item)}>
                      Load in generator
                    </button>
                    <button className="danger" onClick={() => deleteItem(item.id)}>
                      Delete
                    </button>
                  </div>
                </article>
              ))
            )}
          </section>
        )}
      </main>

      {(error || notice) && (
        <div className={`toast ${error ? "toast-error" : "toast-success"}`} role="status">
          <span>{error ? "⚠" : "✓"}</span>
          {error || notice}
        </div>
      )}
    </div>
  );
}

function Select({ label, name, value, values, onChange, disabled }) {
  return (
    <label className="select-field">
      <span>{label}</span>
      <select name={name} value={value} onChange={onChange} disabled={disabled}>
        {values.map((option) => (
          <option key={option} value={option}>
            {name === "tone" ? `${toneMeta[option].icon} ${option}` : option}
          </option>
        ))}
      </select>
    </label>
  );
}


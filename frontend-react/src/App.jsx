import { useCallback, useEffect, useState } from "react";

const API_URL = import.meta.env.VITE_API_URL || "/api";
const initialForm = { input_text: "", message_type: "Email", tone: "Formal", language: "English", length: "Medium" };
const options = {
  message_type: ["Email", "Message"],
  tone: ["Formal", "Professional", "Casual", "Friendly", "Polite", "Apologetic", "Urgent"],
  language: ["English", "Tamil", "Hindi"],
  length: ["Short", "Medium", "Detailed"]
};
const toneMeta = {
  Formal: { icon: "\u{1F3A9}", color: "formal" }, Professional: { icon: "\u{1F4BC}", color: "professional" },
  Casual: { icon: "\u{1F60A}", color: "casual" }, Friendly: { icon: "\u{1F324}\u{FE0F}", color: "friendly" },
  Polite: { icon: "\u{1F64F}", color: "polite" }, Apologetic: { icon: "\u{1F647}", color: "apologetic" },
  Urgent: { icon: "\u{26A1}", color: "urgent" }
};

async function request(path, init) {
  const response = await fetch(`${API_URL}${path}`, init);
  const payload = await response.json().catch(() => ({}));
  if (!response.ok || payload.success === false) throw new Error(payload.error || "Request failed.");
  return payload;
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

  const fetchHistory = useCallback(async (tone = historyTone, type = historyType) => {
    try {
      const params = new URLSearchParams();
      if (tone !== "All") params.set("tone", tone);
      if (type !== "All") params.set("type", type);
      const query = params.toString();
      const result = await request(`/history${query ? `?${query}` : ""}`);
      setHistory(result.data || []);
    } catch (err) { setError(`Unable to load history: ${err.message}`); }
  }, [historyTone, historyType]);

  useEffect(() => { fetchHistory(); }, [fetchHistory]);
  useEffect(() => {
    if (!notice && !error) return undefined;
    const timeout = window.setTimeout(() => { setNotice(""); setError(""); }, 3000);
    return () => window.clearTimeout(timeout);
  }, [notice, error]);

  const updateForm = (event) => {
    const { name, value } = event.target;
    setForm((current) => ({ ...current, [name]: value }));
  };

  const generate = async () => {
    if (!form.input_text.trim()) { setError("Please enter a message to transform."); return; }
    setLoading(true); setError(""); setNotice("");
    try {
      const result = await request("/generate", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ ...form, input_text: form.input_text.trim() }) });
      setOutput(result.data.generated_text); setNotice("Message generated successfully."); fetchHistory();
    } catch (err) { setError(err.message); }
    finally { setLoading(false); }
  };

  const deleteItem = async (id) => {
    if (!window.confirm("Delete this history item?")) return;
    try { await request(`/history/${id}`, { method: "DELETE" }); setNotice("History item deleted."); fetchHistory(); }
    catch (err) { setError(err.message); }
  };

  const clearHistory = async () => {
    if (!window.confirm("Clear all saved history?")) return;
    try { await request("/history", { method: "DELETE" }); setHistory([]); setNotice("History cleared."); }
    catch (err) { setError(err.message); }
  };

  const copyOutput = async () => {
    try { await navigator.clipboard.writeText(output); setNotice("Copied to clipboard."); }
    catch { setError("Unable to copy the generated message."); }
  };

  return <div className="app-shell" data-theme={theme}>
    <aside className="sidebar" aria-label="Generation history">
      <div className="brand"><span className="brand-mark">TG</span><div><strong>Tone Generator</strong><small>AI writing assistant</small></div></div>
      <div className="sidebar-heading"><span>History</span><button className="icon-button" onClick={() => fetchHistory()} aria-label="Refresh history">↻</button></div>
      <div className="history-filters">
        <label><span>Tone</span><select value={historyTone} onChange={(event) => setHistoryTone(event.target.value)}><option>All</option>{options.tone.map((tone) => <option key={tone}>{tone}</option>)}</select></label>
        <label><span>Type</span><select value={historyType} onChange={(event) => setHistoryType(event.target.value)}><option>All</option>{options.message_type.map((type) => <option key={type}>{type}</option>)}</select></label>
      </div>
      <button className="clear-history" onClick={clearHistory}>Clear history</button>
      <div className="sidebar-history">{history.length === 0 ? <div className="sidebar-empty"><span>◷</span><p>No generations yet.<br />Your saved messages will appear here.</p></div> : history.slice(0, 10).map((item) => <button key={item.id} className={`history-link tone-${toneMeta[item.tone]?.color || "formal"}`} onClick={() => { setOutput(item.generated_text); setActiveTab("generator"); }}><div className="history-meta"><span>{item.message_type}</span><span>{toneMeta[item.tone]?.icon} {item.tone}</span></div><strong>{item.input_text.slice(0, 56)}{item.input_text.length > 56 ? "…" : ""}</strong></button>)}</div>
    </aside>
    <main className="page">
      <button className="theme-toggle" onClick={() => setTheme(theme === "light" ? "dark" : "light")} aria-label={`Switch to ${theme === "light" ? "dark" : "light"} theme`}>{theme === "light" ? "☾" : "☀"}</button>
      <header className="hero"><p className="eyebrow">TONE-BASED WRITING</p><h1>Tone-Based Email &amp; Message Generator</h1><p>Turn a rough thought into a clear, polished message in the tone and language you need.</p></header>
      <div className="tabs"><button className={activeTab === "generator" ? "active" : ""} onClick={() => setActiveTab("generator")}>Create message</button><button className={activeTab === "history" ? "active" : ""} onClick={() => setActiveTab("history")}>Saved history</button></div>
      {activeTab === "generator" ? <>
        <section className="input-card"><div className="field-heading"><label htmlFor="input_text">What would you like to say?</label><span>Start with a rough message—we will refine it.</span></div><textarea className={error && !form.input_text.trim() ? "has-error" : ""} id="input_text" name="input_text" value={form.input_text} onChange={updateForm} placeholder="Example: I need to take leave tomorrow because of a family function." rows="7" /><p className="character-count">{form.input_text.length} / 3000</p></section>
        <section className="settings-card"><div className="card-title"><h2>Message settings</h2><p>Choose how your message should sound.</p></div><div className="form-grid"><Select label="Type" name="message_type" value={form.message_type} onChange={updateForm} values={options.message_type} /><Select label="Tone" name="tone" value={form.tone} onChange={updateForm} values={options.tone} /><Select label="Language" name="language" value={form.language} onChange={updateForm} values={options.language} /><Select label="Length" name="length" value={form.length} onChange={updateForm} values={options.length} /></div></section>
        <div className="actions"><button className="primary" onClick={generate} disabled={loading}>{loading ? <><span className="spinner" />Generating</> : "Generate message"}</button><button className="secondary" onClick={() => { setForm(initialForm); setOutput(""); setError(""); }}>Clear</button></div>
        {loading && !output && <section className="output-card output-skeleton" aria-label="Generating message" aria-busy="true"><div className="skeleton-heading" /><div className="skeleton-line wide" /><div className="skeleton-line" /><div className="skeleton-line medium" /><div className="skeleton-line short" /></section>}
        {output && <section className={`output-card output-ready tone-${toneMeta[form.tone].color}`}><div className="output-heading"><div><p className="section-label">GENERATED OUTPUT</p><h2>Ready to send</h2></div><span>{toneMeta[form.tone].icon} {form.tone}</span></div><pre>{output}</pre><p className="character-count output-count">{output.length} characters</p><div className="output-footer"><button className="secondary" onClick={copyOutput}>Copy</button><button className="secondary" onClick={generate} disabled={loading}>Regenerate</button></div></section>}
      </> : <section className="history-panel"><div className="history-title"><div><p className="section-label">YOUR SAVED MESSAGES</p><h2>Generation history</h2></div><button className="secondary" onClick={() => fetchHistory()}>Refresh</button></div>{history.length === 0 ? <div className="empty-state"><span>◷</span><h3>No history yet</h3><p>Generated messages will be saved here for easy access.</p></div> : history.map((item) => <article className={`history-card tone-${toneMeta[item.tone]?.color || "formal"}`} key={item.id}><div className="history-card-top"><div className="badges"><span>{item.message_type}</span><span>{toneMeta[item.tone]?.icon} {item.tone}</span><span>{item.language}</span><span>{item.length}</span></div><small>{item.created_at}</small></div><p><strong>Original:</strong> {item.input_text}</p><pre>{item.generated_text}</pre><div className="output-footer"><button className="secondary" onClick={() => { setOutput(item.generated_text); setActiveTab("generator"); }}>Load output</button><button className="danger" onClick={() => deleteItem(item.id)}>Delete</button></div></article>)}</section>}
    </main>
    {(error || notice) && <div className={`toast ${error ? "toast-error" : "toast-success"}`} role="status"><span>{error ? "⚠" : "✓"}</span>{error || notice}</div>}
  </div>;
}

function Select({ label, name, value, values, onChange }) {
  return <label className="select-field"><span>{label}</span><select name={name} value={value} onChange={onChange}>{values.map((option) => <option key={option} value={option}>{name === "tone" ? `${toneMeta[option].icon} ${option}` : option}</option>)}</select></label>;
}

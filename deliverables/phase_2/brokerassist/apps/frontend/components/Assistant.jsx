"use client";
import { useState, useRef, useEffect } from "react";
import { useLang } from "../lib/i18n";
import { sendChat } from "../lib/api";

export default function Assistant() {
  const { lang, t } = useLang();
  const [open, setOpen] = useState(false);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [msgs, setMsgs] = useState([{ role: "bot", text: t("w_greet") }]);
  const bodyRef = useRef(null);

  useEffect(() => {
    // Keep the greeting in sync with the active language until the user has chatted.
    setMsgs((m) => (m.length === 1 && m[0].role === "bot" ? [{ role: "bot", text: t("w_greet") }] : m));
  }, [lang]); // eslint-disable-line

  useEffect(() => { if (bodyRef.current) bodyRef.current.scrollTop = bodyRef.current.scrollHeight; });

  useEffect(() => {
    const handler = (e) => { setOpen(true); ask(e.detail); };
    window.addEventListener("ba-ask", handler);
    return () => window.removeEventListener("ba-ask", handler);
  }, [lang]); // eslint-disable-line

  async function ask(text) {
    const q = (text ?? input).trim();
    if (!q || busy) return;
    setInput("");
    setMsgs((m) => [...m, { role: "user", text: q }]);
    setBusy(true);
    try {
      const res = await sendChat(q, lang);
      setMsgs((m) => [...m, {
        role: "bot", text: res.answer, branch: res.branch,
        citations: res.citations || [], disclaimer: res.disclaimer,
      }]);
    } catch (e) {
      setMsgs((m) => [...m, { role: "bot", text: t("w_offline"), error: true }]);
    } finally { setBusy(false); }
  }

  return (
    <>
      <button className="assist-launch" aria-label="Open assistant" onClick={() => setOpen((o) => !o)}>
        <i className="ti ti-message-chatbot" aria-hidden="true" />
      </button>
      {open && (
        <div className="assist-panel" role="dialog" aria-label="Assistant">
          <div className="assist-head">
            <span className="t">{t("w_title")}</span>
            <button aria-label="Close" onClick={() => setOpen(false)}><i className="ti ti-x" /></button>
          </div>
          <div className="assist-body" ref={bodyRef} aria-live="polite">
            {msgs.map((m, i) => (
              <div key={i} className={`bubble ${m.role}`}>
                {m.text}
                {m.branch && <span className="badge2">{m.branch}</span>}
                {m.citations && m.citations.length > 0 && (
                  <div className="cites">
                    {m.citations.map((c, j) => (
                      <a key={j} className="cite" href={c.url} target="_blank" rel="noreferrer">
                        <i className="ti ti-file-text" /> {t("src_prefix")}: {c.title} ({c.source})
                      </a>
                    ))}
                  </div>
                )}
                {m.disclaimer && <div className="disclaimer">{m.disclaimer}</div>}
              </div>
            ))}
            {busy && <div className="typing"><span /><span /><span /></div>}
          </div>
          <div className="assist-foot">
            <input value={input} placeholder={t("w_ph")} aria-label="Message"
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && ask()} />
            <button aria-label="Send" onClick={() => ask()}><i className="ti ti-arrow-up" /></button>
          </div>
          <div className="assist-human"><a href="/contact">{t("w_human")}</a></div>
        </div>
      )}
    </>
  );
}

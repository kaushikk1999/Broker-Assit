"use client";
import { useState } from "react";
import { useLang } from "../../lib/i18n";

export default function Contact() {
  const { t } = useLang();
  const [sent, setSent] = useState(false);
  return (
    <section className="hero wrap">
      <span className="eyebrow">Book a demo</span>
      <h1>{t("contact_h1")}</h1>
      <p className="lead">{t("contact_lead")}</p>
      {sent ? (
        <p className="note">Thanks! This is a prototype, so nothing was sent.</p>
      ) : (
        <form onSubmit={(e) => { e.preventDefault(); setSent(true); }}>
          <div className="field"><label htmlFor="n">Full name</label><input id="n" required /></div>
          <div className="field"><label htmlFor="e">Work email</label><input id="e" type="email" required /></div>
          <div className="field"><label htmlFor="b">Brokerage</label><input id="b" required /></div>
          <button className="btn btn-primary" type="submit">{t("cta_book")}</button>
        </form>
      )}
    </section>
  );
}

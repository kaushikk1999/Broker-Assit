"use client";
import Link from "next/link";
import { useLang } from "../lib/i18n";

const LANGS = [["en", "EN"], ["hi", "हिं"], ["ta", "தமிழ்"]];

export default function Header() {
  const { lang, setLang, t } = useLang();
  return (
    <header className="site">
      <nav className="nav">
        <Link href="/" className="brand"><span className="dot" />BrokerAssist</Link>
        <div className="links">
          <Link href="/">{t("nav_home")}</Link>
          <Link href="/stock-research">{t("nav_stock")}</Link>
          <Link href="/nalco">{t("nav_nalco")}</Link>
          <Link href="/algo-education">{t("nav_algo")}</Link>
          <Link href="/contact">{t("nav_contact")}</Link>
        </div>
        <div className="langsw" role="group" aria-label="Language">
          {LANGS.map(([code, label]) => (
            <button key={code} onClick={() => setLang(code)}
              aria-pressed={lang === code} className={lang === code ? "on" : ""}>{label}</button>
          ))}
        </div>
        <Link href="/contact" className="btn btn-primary btn-sm">{t("cta_book")}</Link>
      </nav>
    </header>
  );
}

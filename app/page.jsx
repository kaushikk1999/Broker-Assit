"use client";
import Link from "next/link";
import { useLang } from "../lib/i18n";
import AskButton from "../components/AskButton";

export default function Home() {
  const { t } = useLang();
  const diffs = [["ti-language", "d1t", "d1d"], ["ti-quote", "d2t", "d2d"],
                 ["ti-chart-candle", "d3t", "d3d"], ["ti-code", "d4t", "d4d"]];
  const stats = [["stat1n", "stat1l"], ["stat2n", "stat2l"], ["stat3n", "stat3l"]];
  return (
    <>
      <section className="hero wrap">
        <span className="eyebrow">Multilingual · Cited · Embeddable</span>
        <h1>{t("home_h1")}</h1>
        <p className="lead">{t("home_lead")}</p>
        <div className="cta-row">
          <Link href="/contact" className="btn btn-primary">{t("cta_book")}</Link>
          <AskButton query="Explain NALCO latest quarterly result">{t("cta_try")}</AskButton>
        </div>
      </section>

      <section className="surface">
        <div className="wrap grid cols-4">
          {diffs.map(([ic, ti, di]) => (
            <div className="card" key={ti}>
              <i className={`ti ${ic} ic`} aria-hidden="true" />
              <h3>{t(ti)}</h3><p>{t(di)}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="wrap">
        <div className="stat-grid">
          {stats.map(([n, l]) => (
            <div key={l}>
              <div className="stat-num">{t(n)}</div>
              <div className="stat-l">{t(l)}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="wrap">
        <div className="band">
          <h2>{t("band_t")}</h2>
          <p>{t("band_s")}</p>
          <Link href="/contact" className="btn">{t("cta_book")}</Link>
        </div>
      </section>
    </>
  );
}

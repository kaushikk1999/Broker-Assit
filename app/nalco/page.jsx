"use client";
import { useLang } from "../../lib/i18n";
import AskButton from "../../components/AskButton";

export default function Nalco() {
  const { t } = useLang();
  return (
    <section className="hero wrap">
      <span className="eyebrow">Capability demo</span>
      <h1>{t("nalco_h1")}</h1>
      <p className="lead">{t("nalco_lead")}</p>
      <p className="note">{t("nalco_note")}</p>
      <div className="cta-row">
        <AskButton query="Explain NALCO latest quarterly result" className="btn btn-primary">
          {t("cta_try")}
        </AskButton>
        <AskButton query="What is NALCO's dividend history?">NALCO dividend</AskButton>
      </div>
    </section>
  );
}

"use client";
import { useLang } from "../../lib/i18n";
import AskButton from "../../components/AskButton";

export default function Stock() {
  const { t } = useLang();
  return (
    <section className="hero wrap">
      <span className="eyebrow">Capability demo</span>
      <h1>{t("stock_h1")}</h1>
      <p className="lead">{t("stock_lead")}</p>
      <div className="cta-row">
        <AskButton query="What is the LTP of NALCO?" className="btn btn-primary">{t("cta_try")}</AskButton>
        <AskButton query="What is the LTP of TCS?">TCS price</AskButton>
      </div>
    </section>
  );
}

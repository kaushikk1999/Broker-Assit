"use client";
import { useLang } from "../../lib/i18n";
import AskButton from "../../components/AskButton";

export default function Algo() {
  const { t } = useLang();
  return (
    <section className="hero wrap">
      <span className="eyebrow">Capability demo</span>
      <h1>{t("algo_h1")}</h1>
      <p className="lead">{t("algo_lead")}</p>
      <div className="cta-row">
        <AskButton query="What is the difference between white box and black box algos?"
          className="btn btn-primary">{t("cta_try")}</AskButton>
      </div>
    </section>
  );
}

import "./globals.css";
import { LangProvider } from "../lib/i18n";
import Header from "../components/Header";
import Assistant from "../components/Assistant";

export const metadata = {
  title: "BrokerAssist — Multilingual AI assistant for brokerages",
  description: "Phase 2 pilot: multilingual, citation-backed embeddable assistant.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="" />
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&family=Noto+Sans:wght@400;600&family=Noto+Sans+Devanagari:wght@400;600&family=Noto+Sans+Tamil:wght@400;600&display=swap" />
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@3/dist/tabler-icons.min.css" />
      </head>
      <body>
        <LangProvider>
          <Header />
          <main id="main">{children}</main>
          <footer className="site-footer">
            <div className="wrap">
              <strong>BrokerAssist</strong> · Phase 2 pilot prototype · Informational only — not investment advice.
            </div>
          </footer>
          <Assistant />
        </LangProvider>
      </body>
    </html>
  );
}

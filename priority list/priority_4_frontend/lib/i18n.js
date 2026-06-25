"use client";
// Ported EN/HI/TA dictionary from the Phase 1 prototype (subset for the Next.js port).
import { createContext, useContext, useEffect, useState } from "react";

export const DICT = {
  en: {
    nav_home: "Home", nav_stock: "Stock Research", nav_nalco: "NALCO Intelligence",
    nav_algo: "Algo Education", nav_contact: "Contact", cta_book: "Book a demo", cta_try: "Try the assistant",
    home_h1: "Multilingual, citation-backed AI assistant for brokerages",
    home_lead: "Deflect support tickets and explain stocks, filings and algos — in English, Hindi and Tamil. One snippet to embed.",
    d1t: "Hindi + Tamil finance", d1d: "Answers no incumbent offers today.",
    d2t: "Cited answers", d2d: "Every reply shows the source it came from.",
    d3t: "Finance-domain depth", d3d: "Stocks, filings, NALCO disclosure, algo education.",
    d4t: "Drop-in embeddable", d4d: "Per-brokerage API key + domain allowlist.",
    nalco_h1: "Turn dense filings into plain answers",
    nalco_lead: "Ask about a NALCO disclosure and get a plain-language summary with a link to the source.",
    nalco_note: "Demo uses illustrative data until live NALCO IR sources are connected.",
    stock_h1: "Stock information investors can actually understand",
    stock_lead: "Live prices and results, explained in plain language, in three languages.",
    algo_h1: "Safe, regulation-cited algo learning",
    algo_lead: "SEBI/NSE algo rules — white-box vs black-box — explained with citations.",
    contact_h1: "Book a demo or request access",
    contact_lead: "Tell us about your brokerage and we'll set up a walkthrough and your API key.",
    try_examples: "Try", w_title: "Assistant", w_greet: "Hi! Ask me about stocks, filings or algo trading.",
    w_ph: "Type a message…", w_human: "Talk to a human", src_prefix: "Source",
    w_offline: "Backend not reachable — start the API on :8200.",
    stat1n: "3", stat1l: "languages, out of the box",
    stat2n: "100%", stat2l: "of answers carry a citation",
    stat3n: "0", stat3l: "rivals with Tamil finance support",
    band_t: "See it answer in your investors' language",
    band_s: "Book a 20-minute demo and try it on your own questions.",
  },
  hi: {
    nav_home: "होम", nav_stock: "स्टॉक रिसर्च", nav_nalco: "NALCO इंटेलिजेंस",
    nav_algo: "एल्गो शिक्षा", nav_contact: "संपर्क", cta_book: "डेमो बुक करें", cta_try: "असिस्टेंट आज़माएँ",
    home_h1: "ब्रोकरेज के लिए बहुभाषी, स्रोत-सहित AI असिस्टेंट",
    home_lead: "सपोर्ट टिकट कम करें और स्टॉक, फाइलिंग व एल्गो समझाएँ — अंग्रेज़ी, हिंदी और तमिल में।",
    d1t: "हिंदी + तमिल फाइनेंस", d1d: "जो आज किसी के पास नहीं।",
    d2t: "स्रोत-सहित उत्तर", d2d: "हर उत्तर अपना स्रोत दिखाता है।",
    d3t: "फाइनेंस की गहराई", d3d: "स्टॉक, फाइलिंग, NALCO, एल्गो।",
    d4t: "आसान एम्बेड", d4d: "प्रति-ब्रोकरेज API key + डोमेन अनुमति।",
    nalco_h1: "घनी फाइलिंग को सरल उत्तरों में बदलें",
    nalco_lead: "किसी NALCO डिस्क्लोज़र के बारे में पूछें और स्रोत लिंक सहित सरल सारांश पाएँ।",
    nalco_note: "लाइव NALCO IR स्रोत जुड़ने तक डेमो उदाहरण डेटा का उपयोग करता है।",
    stock_h1: "स्टॉक जानकारी जो निवेशक वाकई समझ सकें",
    stock_lead: "लाइव कीमतें और परिणाम, सरल भाषा में, तीन भाषाओं में।",
    algo_h1: "सुरक्षित, नियम-उद्धृत एल्गो सीखना",
    algo_lead: "SEBI/NSE एल्गो नियम — व्हाइट-बॉक्स बनाम ब्लैक-बॉक्स — उद्धरण सहित।",
    contact_h1: "डेमो बुक करें या एक्सेस का अनुरोध करें",
    contact_lead: "हमें अपनी ब्रोकरेज के बारे में बताएँ और हम वॉकथ्रू व API key सेट करेंगे।",
    try_examples: "आज़माएँ", w_title: "असिस्टेंट", w_greet: "नमस्ते! स्टॉक, फाइलिंग या एल्गो ट्रेडिंग के बारे में पूछें।",
    w_ph: "संदेश लिखें…", w_human: "किसी व्यक्ति से बात करें", src_prefix: "स्रोत",
    w_offline: "बैकएंड उपलब्ध नहीं — :8200 पर API चालू करें।",
    stat1n: "3", stat1l: "भाषाएँ, शुरू से",
    stat2n: "100%", stat2l: "उत्तरों में स्रोत उद्धरण",
    stat3n: "0", stat3l: "प्रतिद्वंद्वी जिनके पास तमिल फाइनेंस है",
    band_t: "इसे अपने निवेशकों की भाषा में उत्तर देते देखें",
    band_s: "20-मिनट का डेमो बुक करें और अपने सवालों पर आज़माएँ।",
  },
  ta: {
    nav_home: "முகப்பு", nav_stock: "பங்கு ஆராய்ச்சி", nav_nalco: "NALCO நுண்ணறிவு",
    nav_algo: "அல்கோ கல்வி", nav_contact: "தொடர்பு", cta_book: "டெமோ பதிவு செய்", cta_try: "உதவியாளரை முயற்சி",
    home_h1: "ப்ரோக்கரேஜ்களுக்கான பன்மொழி, ஆதார-அடிப்படையிலான AI உதவியாளர்",
    home_lead: "ஆதரவு கோரிக்கைகளைக் குறைத்து பங்குகள், தாக்கல்கள், அல்கோவை விளக்குங்கள் — ஆங்கிலம், இந்தி, தமிழில்.",
    d1t: "இந்தி + தமிழ் நிதி", d1d: "இன்று யாரிடமும் இல்லாதது.",
    d2t: "ஆதாரத்துடன் பதில்", d2d: "ஒவ்வொரு பதிலும் அதன் ஆதாரத்தைக் காட்டுகிறது.",
    d3t: "நிதி ஆழம்", d3d: "பங்கு, தாக்கல், NALCO, அல்கோ.",
    d4t: "எளிதாக இணைக்க", d4d: "ஒவ்வொரு ப்ரோக்கருக்கும் API key + டொமைன் அனுமதி.",
    nalco_h1: "அடர்த்தியான தாக்கல்களை எளிய பதில்களாக மாற்றுங்கள்",
    nalco_lead: "ஒரு NALCO வெளிப்பாடு பற்றி கேளுங்கள், ஆதார இணைப்புடன் எளிய சுருக்கம் பெறுங்கள்.",
    nalco_note: "நேரலை NALCO IR ஆதாரங்கள் இணைக்கும் வரை டெமோ எடுத்துக்காட்டு தரவைப் பயன்படுத்துகிறது.",
    stock_h1: "முதலீட்டாளர்கள் புரிந்துகொள்ளும் பங்கு தகவல்",
    stock_lead: "நேரலை விலைகள், முடிவுகள், எளிய மொழியில், மூன்று மொழிகளில்.",
    algo_h1: "பாதுகாப்பான, விதி-மேற்கோள் அல்கோ கற்றல்",
    algo_lead: "SEBI/NSE அல்கோ விதிகள் — வைட்-பாக்ஸ் vs பிளாக்-பாக்ஸ் — மேற்கோள்களுடன்.",
    contact_h1: "டெமோவைப் பதிவு செய்யுங்கள் அல்லது அணுகலைக் கோருங்கள்",
    contact_lead: "உங்கள் ப்ரோக்கரேஜ் பற்றி சொல்லுங்கள், நாங்கள் வாக்த்ரூ மற்றும் API key அமைப்போம்.",
    try_examples: "முயற்சி", w_title: "உதவியாளர்", w_greet: "வணக்கம்! பங்குகள், தாக்கல்கள் அல்லது அல்கோ வர்த்தகம் பற்றி கேளுங்கள்.",
    w_ph: "செய்தியை உள்ளிடவும்…", w_human: "ஒரு நபரிடம் பேசு", src_prefix: "ஆதாரம்",
    w_offline: "பின்தளம் கிடைக்கவில்லை — :8200 இல் API ஐத் தொடங்கவும்.",
    stat1n: "3", stat1l: "மொழிகள், ஆரம்பத்திலிருந்தே",
    stat2n: "100%", stat2l: "பதில்களில் ஆதார மேற்கோள்",
    stat3n: "0", stat3l: "தமிழ் நிதி ஆதரவுள்ள போட்டியாளர்கள்",
    band_t: "உங்கள் முதலீட்டாளர்களின் மொழியில் பதிலளிப்பதைப் பாருங்கள்",
    band_s: "20-நிமிட டெமோவைப் பதிவு செய்து உங்கள் கேள்விகளில் முயற்சிக்கவும்.",
  },
};

const LangCtx = createContext({ lang: "en", setLang: () => {}, t: (k) => k });

export function LangProvider({ children }) {
  const [lang, setLang] = useState("en");
  useEffect(() => {
    const saved = typeof window !== "undefined" && localStorage.getItem("ba_lang");
    if (saved && DICT[saved]) setLang(saved);
  }, []);
  useEffect(() => {
    if (typeof document !== "undefined") document.documentElement.lang = lang;
    if (typeof window !== "undefined") localStorage.setItem("ba_lang", lang);
  }, [lang]);
  const t = (k) => (DICT[lang] && DICT[lang][k]) || DICT.en[k] || k;
  return <LangCtx.Provider value={{ lang, setLang, t }}>{children}</LangCtx.Provider>;
}

export const useLang = () => useContext(LangCtx);

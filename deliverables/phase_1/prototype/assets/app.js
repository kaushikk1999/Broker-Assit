/* BrokerAssist Phase 1.5 prototype — i18n + shared chrome + mock assistant. No backend. */
(function () {
  "use strict";

  var I18N = {
    en: {
      nav_home:"Home", nav_stock:"Stock Research", nav_nalco:"NALCO Intelligence",
      nav_algo:"Algo Education", nav_contact:"Contact", nav_pricing:"Pricing", pricing_soon:"Soon",
      cta_book:"Book a demo", cta_try:"Try the assistant",
      footer_tag:"Multilingual, citation-backed AI assistant for brokerages.",
      footer_disclaimer:"Informational only. Not investment advice. Demo content; figures are illustrative.",
      footer_rights:"© 2026 BrokerAssist · Phase 1.5 prototype",
      w_title:"Assistant", w_greet:"Hi! Ask me about stocks, filings or algo trading.",
      w_input_ph:"Type a message…", w_human:"Talk to a human",
      w_disclaimer:"Informational only — not investment advice.",
      w_fullscreen:"Full screen", w_close:"Close", w_send:"Send", src_prefix:"Source",
      ans_nalco:"NALCO reported higher revenue this quarter, led by stronger alumina realisations. Net profit rose versus the prior quarter.",
      src_nalco:"NSE filing — quarterly results",
      ans_stock:"The stock last traded around its 3-month average. Volumes were steady and the P/E sits broadly in line with sector peers.",
      src_stock:"Exchange market data",
      ans_algo:"A white-box algo discloses its logic to you; a black-box algo does not. Under SEBI/NSE rules, black-box providers must register as Research Analysts and algos must be hosted on the broker's server.",
      src_algo:"NSE FAQ — retail algo trading",
      ans_generic:"I can help with stock information, filing explanations, and algo-trading education — all with sources. Try asking about a stock, a NALCO filing, or white-box vs black-box algos.",
      home_eyebrow:"Multilingual · cited · embeddable",
      home_h1:"Multilingual, citation-backed AI assistant for brokerages",
      home_lead:"Deflect support tickets and explain stocks, filings and algos — in English, Hindi and Tamil. One snippet to embed.",
      d1t:"Hindi + Tamil finance", d1d:"Finance answers no incumbent offers today.",
      d2t:"Cited answers", d2d:"Every reply shows the source it came from.",
      d3t:"Finance-domain depth", d3d:"Stocks, filings, NALCO disclosure, algo education.",
      d4t:"Drop-in embeddable", d4d:"Per-brokerage API key + domain allowlist.",
      how_title:"Live on your site in three steps",
      how_1:"Request an API key and allowlist your domain.",
      how_2:"Add one script snippet to your site.",
      how_3:"Investors get cited answers in EN / हिं / தமிழ்.",
      how_code_caption:"That is the whole embed.",
      proof_title:"Built for the gap no one fills",
      p1n:"0", p1l:"competitors with Tamil finance support",
      p2n:"100%", p2l:"of answers carry a source citation",
      p3n:"3", p3l:"languages out of the box",
      band_title:"See it answer in your investors' language",
      band_sub:"Book a 20-minute demo and try it on your own questions.",
      demo_label:"Live demo — try it",
      demoq_home:"Explain NALCO's latest quarterly result",
      stock_eyebrow:"Capability demo",
      stock_h1:"Stock information investors can actually understand",
      stock_lead:"Live prices, results and ratios — explained in plain language, with a source, in three languages.",
      stock_demo_label:"This is the live assistant — ask it",
      sq:"How did the stock do this quarter?",
      stock_prompts_title:"Try asking",
      sp1:"What was the latest result?", sp2:"How does the P/E compare to peers?", sp3:"Explain this in Tamil",
      stock_caps_title:"What it covers",
      sc1:"Live and last-traded prices", sc2:"Quarterly and annual results",
      sc3:"Key ratios vs sector peers", sc4:"Plain-language explanations, cited",
      nalco_eyebrow:"Capability demo",
      nalco_h1:"Turn dense filings into plain answers",
      nalco_lead:"Ask about a NALCO disclosure and get a plain-language summary with the figures — and a link to the source filing.",
      nalco_note:"Demo uses illustrative data until live NALCO investor-relations sources are connected.",
      nq:"Explain NALCO's latest quarterly result",
      nalco_caps_title:"What it covers",
      nc1:"Plain-language filing summaries", nc2:"Key figures pulled from disclosures",
      nc3:"Every answer linked to its source",
      algo_eyebrow:"Capability demo",
      algo_h1:"Safe, regulation-cited algo learning",
      algo_lead:"Explains SEBI/NSE algo-trading rules — white-box vs black-box, empanelment, hosting — with citations and a compliance disclaimer.",
      aq:"What's the difference between white-box and black-box algos?",
      algo_disc:"Educational content based on NSE/SEBI circulars. Not a recommendation to trade.",
      algo_topics_title:"Topics covered",
      at1:"White-box vs black-box algos", at2:"Algo-provider empanelment criteria",
      at3:"Hosting on the broker's server", at4:"Static IP and RA requirements",
      contact_eyebrow:"Book a demo",
      contact_h1:"Book a demo or request access",
      contact_lead:"Tell us about your brokerage and we'll set up a walkthrough and your API key.",
      f_name:"Full name", f_email:"Work email", f_broker:"Brokerage name", f_size:"Size",
      f_size_s:"Up to 50k clients", f_size_m:"50k–500k clients", f_size_l:"500k+ clients",
      f_langs:"Languages needed", f_lang_en:"English", f_lang_hi:"Hindi", f_lang_ta:"Tamil",
      f_usecase:"What do you want the assistant to do?", f_submit:"Request access",
      what_title:"What you get", what_1:"API key + domain allowlist", what_2:"EN / हिं / தமிழ் out of the box",
      what_3:"Cited answers + human handoff",
      contact_success:"Thanks! This is a prototype, so nothing was sent. In production we'd email your API key and book the demo."
    },
    hi: {
      nav_home:"होम", nav_stock:"स्टॉक रिसर्च", nav_nalco:"NALCO इंटेलिजेंस",
      nav_algo:"एल्गो शिक्षा", nav_contact:"संपर्क", nav_pricing:"मूल्य", pricing_soon:"जल्द",
      cta_book:"डेमो बुक करें", cta_try:"असिस्टेंट आज़माएँ",
      footer_tag:"ब्रोकरेज के लिए बहुभाषी, स्रोत-सहित AI असिस्टेंट।",
      footer_disclaimer:"केवल जानकारी के लिए। निवेश सलाह नहीं। डेमो सामग्री; आंकड़े उदाहरणस्वरूप हैं।",
      footer_rights:"© 2026 BrokerAssist · फेज़ 1.5 प्रोटोटाइप",
      w_title:"असिस्टेंट", w_greet:"नमस्ते! स्टॉक, फाइलिंग या एल्गो ट्रेडिंग के बारे में पूछें।",
      w_input_ph:"संदेश लिखें…", w_human:"किसी व्यक्ति से बात करें",
      w_disclaimer:"केवल जानकारी के लिए — निवेश सलाह नहीं।",
      w_fullscreen:"फुल स्क्रीन", w_close:"बंद करें", w_send:"भेजें", src_prefix:"स्रोत",
      ans_nalco:"NALCO ने इस तिमाही अधिक राजस्व दर्ज किया, जो बेहतर एल्युमिना कीमतों से प्रेरित था। पिछली तिमाही की तुलना में शुद्ध लाभ बढ़ा।",
      src_nalco:"NSE फाइलिंग — तिमाही परिणाम",
      ans_stock:"स्टॉक अपने 3-महीने के औसत के आसपास कारोबार कर रहा था। वॉल्यूम स्थिर रहा और P/E सेक्टर के समकक्षों के अनुरूप है।",
      src_stock:"एक्सचेंज मार्केट डेटा",
      ans_algo:"व्हाइट-बॉक्स एल्गो अपना लॉजिक आपको बताता है; ब्लैक-बॉक्स नहीं बताता। SEBI/NSE नियमों के तहत ब्लैक-बॉक्स प्रदाता को रिसर्च एनालिस्ट के रूप में पंजीकरण कराना होता है और एल्गो ब्रोकर के सर्वर पर होस्ट होने चाहिए।",
      src_algo:"NSE FAQ — रिटेल एल्गो ट्रेडिंग",
      ans_generic:"मैं स्टॉक जानकारी, फाइलिंग की व्याख्या और एल्गो-ट्रेडिंग शिक्षा में मदद कर सकता हूँ — सभी स्रोत के साथ। किसी स्टॉक, NALCO फाइलिंग, या व्हाइट-बॉक्स बनाम ब्लैक-बॉक्स एल्गो के बारे में पूछें।",
      home_eyebrow:"बहुभाषी · स्रोत-सहित · एम्बेड करने योग्य",
      home_h1:"ब्रोकरेज के लिए बहुभाषी, स्रोत-सहित AI असिस्टेंट",
      home_lead:"सपोर्ट टिकट कम करें और स्टॉक, फाइलिंग व एल्गो समझाएँ — अंग्रेज़ी, हिंदी और तमिल में। बस एक स्निपेट से एम्बेड करें।",
      d1t:"हिंदी + तमिल फाइनेंस", d1d:"फाइनेंस उत्तर जो आज किसी के पास नहीं।",
      d2t:"स्रोत-सहित उत्तर", d2d:"हर उत्तर अपना स्रोत दिखाता है।",
      d3t:"फाइनेंस की गहराई", d3d:"स्टॉक, फाइलिंग, NALCO डिस्क्लोज़र, एल्गो शिक्षा।",
      d4t:"आसान एम्बेड", d4d:"प्रति-ब्रोकरेज API key + डोमेन अनुमति।",
      how_title:"तीन चरणों में आपकी साइट पर लाइव",
      how_1:"API key माँगें और अपना डोमेन अनुमत करें।",
      how_2:"अपनी साइट में एक स्क्रिप्ट स्निपेट जोड़ें।",
      how_3:"निवेशकों को EN / हिं / தமிழ் में स्रोत-सहित उत्तर मिलें।",
      how_code_caption:"बस इतना ही एम्बेड है।",
      proof_title:"उस कमी के लिए जिसे कोई पूरा नहीं करता",
      p1n:"0", p1l:"प्रतिस्पर्धी जिनके पास तमिल फाइनेंस सपोर्ट है",
      p2n:"100%", p2l:"उत्तरों में स्रोत उद्धरण होता है",
      p3n:"3", p3l:"भाषाएँ शुरू से ही",
      band_title:"इसे अपने निवेशकों की भाषा में उत्तर देते देखें",
      band_sub:"20-मिनट का डेमो बुक करें और अपने सवालों पर आज़माएँ।",
      demo_label:"लाइव डेमो — आज़माएँ",
      demoq_home:"NALCO का नवीनतम तिमाही परिणाम समझाएँ",
      stock_eyebrow:"क्षमता डेमो",
      stock_h1:"स्टॉक जानकारी जो निवेशक वाकई समझ सकें",
      stock_lead:"लाइव कीमतें, परिणाम और अनुपात — सरल भाषा में, स्रोत के साथ, तीन भाषाओं में।",
      stock_demo_label:"यह लाइव असिस्टेंट है — इससे पूछें",
      sq:"इस तिमाही स्टॉक कैसा रहा?",
      stock_prompts_title:"पूछकर देखें",
      sp1:"नवीनतम परिणाम क्या था?", sp2:"P/E समकक्षों से कैसे तुलना करता है?", sp3:"इसे तमिल में समझाएँ",
      stock_caps_title:"यह क्या कवर करता है",
      sc1:"लाइव और अंतिम कारोबार कीमतें", sc2:"तिमाही और वार्षिक परिणाम",
      sc3:"सेक्टर समकक्षों बनाम मुख्य अनुपात", sc4:"सरल भाषा व्याख्याएँ, स्रोत-सहित",
      nalco_eyebrow:"क्षमता डेमो",
      nalco_h1:"घनी फाइलिंग को सरल उत्तरों में बदलें",
      nalco_lead:"किसी NALCO डिस्क्लोज़र के बारे में पूछें और आंकड़ों सहित सरल सारांश पाएँ — साथ ही स्रोत फाइलिंग का लिंक।",
      nalco_note:"लाइव NALCO निवेशक-संबंध स्रोत जुड़ने तक डेमो उदाहरण डेटा का उपयोग करता है।",
      nq:"NALCO का नवीनतम तिमाही परिणाम समझाएँ",
      nalco_caps_title:"यह क्या कवर करता है",
      nc1:"सरल भाषा में फाइलिंग सारांश", nc2:"डिस्क्लोज़र से लिए गए मुख्य आंकड़े",
      nc3:"हर उत्तर अपने स्रोत से जुड़ा",
      algo_eyebrow:"क्षमता डेमो",
      algo_h1:"सुरक्षित, नियम-उद्धृत एल्गो सीखना",
      algo_lead:"SEBI/NSE एल्गो-ट्रेडिंग नियम समझाता है — व्हाइट-बॉक्स बनाम ब्लैक-बॉक्स, एम्पैनलमेंट, होस्टिंग — उद्धरण और अनुपालन अस्वीकरण के साथ।",
      aq:"व्हाइट-बॉक्स और ब्लैक-बॉक्स एल्गो में क्या अंतर है?",
      algo_disc:"NSE/SEBI सर्कुलर पर आधारित शैक्षिक सामग्री। ट्रेड करने की सिफारिश नहीं।",
      algo_topics_title:"शामिल विषय",
      at1:"व्हाइट-बॉक्स बनाम ब्लैक-बॉक्स एल्गो", at2:"एल्गो-प्रदाता एम्पैनलमेंट मानदंड",
      at3:"ब्रोकर के सर्वर पर होस्टिंग", at4:"स्टैटिक IP और RA आवश्यकताएँ",
      contact_eyebrow:"डेमो बुक करें",
      contact_h1:"डेमो बुक करें या एक्सेस का अनुरोध करें",
      contact_lead:"हमें अपनी ब्रोकरेज के बारे में बताएँ और हम वॉकथ्रू व आपकी API key सेट करेंगे।",
      f_name:"पूरा नाम", f_email:"कार्य ईमेल", f_broker:"ब्रोकरेज नाम", f_size:"आकार",
      f_size_s:"50 हज़ार ग्राहक तक", f_size_m:"50 हज़ार–5 लाख ग्राहक", f_size_l:"5 लाख+ ग्राहक",
      f_langs:"आवश्यक भाषाएँ", f_lang_en:"अंग्रेज़ी", f_lang_hi:"हिंदी", f_lang_ta:"तमिल",
      f_usecase:"आप असिस्टेंट से क्या कराना चाहते हैं?", f_submit:"एक्सेस का अनुरोध करें",
      what_title:"आपको क्या मिलता है", what_1:"API key + डोमेन अनुमति", what_2:"EN / हिं / தமிழ் शुरू से",
      what_3:"स्रोत-सहित उत्तर + मानव हैंडऑफ",
      contact_success:"धन्यवाद! यह एक प्रोटोटाइप है, इसलिए कुछ भी नहीं भेजा गया। प्रोडक्शन में हम आपकी API key ईमेल करते और डेमो बुक करते।"
    },
    ta: {
      nav_home:"முகப்பு", nav_stock:"பங்கு ஆராய்ச்சி", nav_nalco:"NALCO நுண்ணறிவு",
      nav_algo:"அல்கோ கல்வி", nav_contact:"தொடர்பு", nav_pricing:"விலை", pricing_soon:"விரைவில்",
      cta_book:"டெமோ பதிவு செய்", cta_try:"உதவியாளரை முயற்சி",
      footer_tag:"ப்ரோக்கரேஜ்களுக்கான பன்மொழி, ஆதார-அடிப்படையிலான AI உதவியாளர்.",
      footer_disclaimer:"தகவலுக்காக மட்டுமே. முதலீட்டு ஆலோசனை அல்ல. டெமோ உள்ளடக்கம்; எண்கள் எடுத்துக்காட்டு.",
      footer_rights:"© 2026 BrokerAssist · கட்டம் 1.5 முன்மாதிரி",
      w_title:"உதவியாளர்", w_greet:"வணக்கம்! பங்குகள், தாக்கல்கள் அல்லது அல்கோ வர்த்தகம் பற்றி கேளுங்கள்.",
      w_input_ph:"செய்தியை உள்ளிடவும்…", w_human:"ஒரு நபரிடம் பேசு",
      w_disclaimer:"தகவலுக்காக மட்டுமே — முதலீட்டு ஆலோசனை அல்ல.",
      w_fullscreen:"முழுத்திரை", w_close:"மூடு", w_send:"அனுப்பு", src_prefix:"ஆதாரம்",
      ans_nalco:"NALCO இந்த காலாண்டில் அதிக வருவாயைப் பதிவு செய்தது, வலுவான அலுமினா விலைகளால் இயக்கப்பட்டது. முந்தைய காலாண்டை விட நிகர லாபம் உயர்ந்தது.",
      src_nalco:"NSE தாக்கல் — காலாண்டு முடிவுகள்",
      ans_stock:"பங்கு அதன் 3-மாத சராசரியைச் சுற்றி வர்த்தகமானது. அளவுகள் நிலையாக இருந்தன, P/E துறை சகாக்களுக்கு ஏற்ப உள்ளது.",
      src_stock:"பரிவர்த்தனை சந்தை தரவு",
      ans_algo:"வைட்-பாக்ஸ் அல்கோ அதன் தர்க்கத்தை உங்களுக்கு வெளிப்படுத்துகிறது; பிளாக்-பாக்ஸ் இல்லை. SEBI/NSE விதிகளின் கீழ், பிளாக்-பாக்ஸ் வழங்குநர்கள் ஆராய்ச்சி ஆய்வாளராக பதிவு செய்ய வேண்டும், அல்கோக்கள் ப்ரோக்கரின் சர்வரில் ஹோஸ்ட் செய்யப்பட வேண்டும்.",
      src_algo:"NSE FAQ — சில்லறை அல்கோ வர்த்தகம்",
      ans_generic:"பங்கு தகவல், தாக்கல் விளக்கம், அல்கோ-வர்த்தக கல்வி ஆகியவற்றில் உதவ முடியும் — அனைத்தும் ஆதாரத்துடன். ஒரு பங்கு, NALCO தாக்கல், அல்லது வைட்-பாக்ஸ் vs பிளாக்-பாக்ஸ் அல்கோ பற்றி கேளுங்கள்.",
      home_eyebrow:"பன்மொழி · ஆதாரத்துடன் · இணைக்கக்கூடியது",
      home_h1:"ப்ரோக்கரேஜ்களுக்கான பன்மொழி, ஆதார-அடிப்படையிலான AI உதவியாளர்",
      home_lead:"ஆதரவு கோரிக்கைகளைக் குறைத்து பங்குகள், தாக்கல்கள், அல்கோவை விளக்குங்கள் — ஆங்கிலம், இந்தி, தமிழில். ஒரே ஸ்னிப்பெட்டில் இணைக்கவும்.",
      d1t:"இந்தி + தமிழ் நிதி", d1d:"இன்று யாரிடமும் இல்லாத நிதி பதில்கள்.",
      d2t:"ஆதாரத்துடன் பதில்", d2d:"ஒவ்வொரு பதிலும் அதன் ஆதாரத்தைக் காட்டுகிறது.",
      d3t:"நிதி ஆழம்", d3d:"பங்கு, தாக்கல், NALCO வெளிப்பாடு, அல்கோ கல்வி.",
      d4t:"எளிதாக இணைக்க", d4d:"ஒவ்வொரு ப்ரோக்கருக்கும் API key + டொமைன் அனுமதி.",
      how_title:"மூன்று படிகளில் உங்கள் தளத்தில் நேரலை",
      how_1:"API key கோரி உங்கள் டொமைனை அனுமதிக்கவும்.",
      how_2:"உங்கள் தளத்தில் ஒரு ஸ்கிரிப்ட் ஸ்னிப்பெட்டைச் சேர்க்கவும்.",
      how_3:"முதலீட்டாளர்கள் EN / हिं / தமிழில் ஆதாரத்துடன் பதில் பெறுவார்கள்.",
      how_code_caption:"இதுவே முழு இணைப்பு.",
      proof_title:"யாரும் நிரப்பாத இடைவெளிக்காக",
      p1n:"0", p1l:"போட்டியாளர்களுக்கு தமிழ் நிதி ஆதரவு உள்ளது",
      p2n:"100%", p2l:"பதில்களில் ஆதார மேற்கோள் உள்ளது",
      p3n:"3", p3l:"மொழிகள் ஆரம்பத்திலிருந்தே",
      band_title:"உங்கள் முதலீட்டாளர்களின் மொழியில் பதிலளிப்பதைப் பாருங்கள்",
      band_sub:"20-நிமிட டெமோவைப் பதிவு செய்து உங்கள் கேள்விகளில் முயற்சிக்கவும்.",
      demo_label:"நேரலை டெமோ — முயற்சிக்கவும்",
      demoq_home:"NALCO இன் சமீபத்திய காலாண்டு முடிவை விளக்குங்கள்",
      stock_eyebrow:"திறன் டெமோ",
      stock_h1:"முதலீட்டாளர்கள் உண்மையில் புரிந்துகொள்ளும் பங்கு தகவல்",
      stock_lead:"நேரலை விலைகள், முடிவுகள், விகிதங்கள் — எளிய மொழியில், ஆதாரத்துடன், மூன்று மொழிகளில்.",
      stock_demo_label:"இது நேரலை உதவியாளர் — கேளுங்கள்",
      sq:"இந்த காலாண்டில் பங்கு எப்படி இருந்தது?",
      stock_prompts_title:"கேட்டு முயற்சிக்கவும்",
      sp1:"சமீபத்திய முடிவு என்ன?", sp2:"P/E சகாக்களுடன் எப்படி ஒப்பிடுகிறது?", sp3:"இதை தமிழில் விளக்குங்கள்",
      stock_caps_title:"இது எதை உள்ளடக்கியது",
      sc1:"நேரலை மற்றும் கடைசி வர்த்தக விலைகள்", sc2:"காலாண்டு மற்றும் வருடாந்திர முடிவுகள்",
      sc3:"துறை சகாக்கள் vs முக்கிய விகிதங்கள்", sc4:"எளிய மொழி விளக்கங்கள், ஆதாரத்துடன்",
      nalco_eyebrow:"திறன் டெமோ",
      nalco_h1:"அடர்த்தியான தாக்கல்களை எளிய பதில்களாக மாற்றுங்கள்",
      nalco_lead:"ஒரு NALCO வெளிப்பாடு பற்றி கேளுங்கள், எண்களுடன் எளிய சுருக்கம் பெறுங்கள் — ஆதார தாக்கலுக்கான இணைப்புடன்.",
      nalco_note:"நேரலை NALCO முதலீட்டாளர்-உறவு ஆதாரங்கள் இணைக்கும் வரை டெமோ எடுத்துக்காட்டு தரவைப் பயன்படுத்துகிறது.",
      nq:"NALCO இன் சமீபத்திய காலாண்டு முடிவை விளக்குங்கள்",
      nalco_caps_title:"இது எதை உள்ளடக்கியது",
      nc1:"எளிய மொழியில் தாக்கல் சுருக்கங்கள்", nc2:"வெளிப்பாடுகளில் இருந்து முக்கிய எண்கள்",
      nc3:"ஒவ்வொரு பதிலும் அதன் ஆதாரத்துடன் இணைக்கப்பட்டது",
      algo_eyebrow:"திறன் டெமோ",
      algo_h1:"பாதுகாப்பான, விதி-மேற்கோள் அல்கோ கற்றல்",
      algo_lead:"SEBI/NSE அல்கோ-வர்த்தக விதிகளை விளக்குகிறது — வைட்-பாக்ஸ் vs பிளாக்-பாக்ஸ், பட்டியலிடல், ஹோஸ்டிங் — மேற்கோள்கள் மற்றும் இணக்க மறுப்புடன்.",
      aq:"வைட்-பாக்ஸ் மற்றும் பிளாக்-பாக்ஸ் அல்கோவிற்கு என்ன வித்தியாசம்?",
      algo_disc:"NSE/SEBI சுற்றறிக்கைகளின் அடிப்படையில் கல்வி உள்ளடக்கம். வர்த்தகம் செய்ய பரிந்துரை அல்ல.",
      algo_topics_title:"உள்ளடக்கிய தலைப்புகள்",
      at1:"வைட்-பாக்ஸ் vs பிளாக்-பாக்ஸ் அல்கோ", at2:"அல்கோ-வழங்குநர் பட்டியலிடல் அளவுகோல்கள்",
      at3:"ப்ரோக்கரின் சர்வரில் ஹோஸ்டிங்", at4:"நிலையான IP மற்றும் RA தேவைகள்",
      contact_eyebrow:"டெமோ பதிவு செய்",
      contact_h1:"டெமோவைப் பதிவு செய்யுங்கள் அல்லது அணுகலைக் கோருங்கள்",
      contact_lead:"உங்கள் ப்ரோக்கரேஜ் பற்றி சொல்லுங்கள், நாங்கள் ஒரு வாக்த்ரூ மற்றும் உங்கள் API key ஐ அமைப்போம்.",
      f_name:"முழு பெயர்", f_email:"பணி மின்னஞ்சல்", f_broker:"ப்ரோக்கரேஜ் பெயர்", f_size:"அளவு",
      f_size_s:"50 ஆயிரம் வாடிக்கையாளர்கள் வரை", f_size_m:"50 ஆயிரம்–5 லட்சம் வாடிக்கையாளர்கள்", f_size_l:"5 லட்சம்+ வாடிக்கையாளர்கள்",
      f_langs:"தேவையான மொழிகள்", f_lang_en:"ஆங்கிலம்", f_lang_hi:"இந்தி", f_lang_ta:"தமிழ்",
      f_usecase:"உதவியாளர் என்ன செய்ய வேண்டும்?", f_submit:"அணுகலைக் கோரு",
      what_title:"உங்களுக்கு என்ன கிடைக்கும்", what_1:"API key + டொமைன் அனுமதி", what_2:"EN / हिं / தமிழ் ஆரம்பத்திலிருந்தே",
      what_3:"ஆதாரத்துடன் பதில் + மனித ஒப்படைப்பு",
      contact_success:"நன்றி! இது ஒரு முன்மாதிரி, எனவே எதுவும் அனுப்பப்படவில்லை. உற்பத்தியில் உங்கள் API key ஐ மின்னஞ்சல் செய்து டெமோவைப் பதிவு செய்திருப்போம்."
    }
  };

  var LANGS = ["en", "hi", "ta"];
  var LANG_LABELS = { en: "EN", hi: "हिं", ta: "தமிழ்" };
  var state = { lang: "en" };

  function t(key) { return (I18N[state.lang] && I18N[state.lang][key]) || I18N.en[key] || key; }

  function applyLang(lang) {
    if (LANGS.indexOf(lang) === -1) lang = "en";
    state.lang = lang;
    try { localStorage.setItem("ba_lang", lang); } catch (e) {}
    document.documentElement.setAttribute("lang", lang);
    document.body.setAttribute("lang", lang);
    document.querySelectorAll("[data-i18n]").forEach(function (el) {
      el.textContent = t(el.getAttribute("data-i18n"));
    });
    document.querySelectorAll("[data-i18n-ph]").forEach(function (el) {
      el.setAttribute("placeholder", t(el.getAttribute("data-i18n-ph")));
    });
    document.querySelectorAll(".langsw button").forEach(function (b) {
      b.setAttribute("aria-pressed", b.getAttribute("data-lang") === lang ? "true" : "false");
    });
  }

  function langSwitcher() {
    var d = document.createElement("div");
    d.className = "langsw";
    d.setAttribute("role", "group");
    d.setAttribute("aria-label", "Language");
    LANGS.forEach(function (l) {
      var b = document.createElement("button");
      b.type = "button";
      b.textContent = LANG_LABELS[l];
      b.setAttribute("data-lang", l);
      b.setAttribute("aria-label", l);
      b.addEventListener("click", function () { applyLang(l); });
      d.appendChild(b);
    });
    return d;
  }

  function navLink(href, key, page) {
    var a = document.createElement("a");
    a.href = href;
    a.setAttribute("data-i18n", key);
    a.textContent = t(key);
    if (document.body.dataset.page === page) a.className = "active";
    return a;
  }

  function buildHeader() {
    var skip = document.createElement("a");
    skip.href = "#main"; skip.className = "skip"; skip.textContent = "Skip to content";
    document.body.insertBefore(skip, document.body.firstChild);

    var header = document.createElement("header");
    header.className = "site";
    var nav = document.createElement("div");
    nav.className = "nav wrap";

    var brand = document.createElement("a");
    brand.href = "index.html"; brand.className = "brand";
    brand.innerHTML = '<span class="dot" aria-hidden="true"></span>BrokerAssist';

    var links = document.createElement("nav");
    links.className = "links";
    links.setAttribute("aria-label", "Primary");
    links.appendChild(navLink("index.html", "nav_home", "home"));
    links.appendChild(navLink("stock-research.html", "nav_stock", "stock"));
    links.appendChild(navLink("nalco.html", "nav_nalco", "nalco"));
    links.appendChild(navLink("algo-education.html", "nav_algo", "algo"));
    links.appendChild(navLink("contact.html", "nav_contact", "contact"));
    var pricing = document.createElement("span");
    pricing.style.color = "var(--text-hint)"; pricing.style.fontSize = ".95rem";
    pricing.innerHTML = '<span data-i18n="nav_pricing">Pricing</span> <span class="badge" data-i18n="pricing_soon">Soon</span>';
    links.appendChild(pricing);

    var book = document.createElement("a");
    book.href = "contact.html"; book.className = "btn btn-primary btn-sm";
    book.setAttribute("data-i18n", "cta_book"); book.textContent = t("cta_book");

    nav.appendChild(brand);
    nav.appendChild(links);
    nav.appendChild(langSwitcher());
    nav.appendChild(book);
    header.appendChild(nav);
    document.body.insertBefore(header, skip.nextSibling);
  }

  function buildFooter() {
    var f = document.createElement("footer");
    f.className = "site";
    var row = document.createElement("div");
    row.className = "frow wrap";
    row.innerHTML =
      '<div style="max-width:60ch"><strong>BrokerAssist</strong> · <span data-i18n="footer_tag"></span>' +
      '<br><small data-i18n="footer_disclaimer"></small></div>' +
      '<small data-i18n="footer_rights"></small>';
    f.appendChild(row);
    document.body.appendChild(f);
  }

  /* ---- mock assistant ---- */
  function classify(text) {
    var s = (text || "").toLowerCase();
    if (s.indexOf("nalco") > -1) return "nalco";
    if (s.indexOf("algo") > -1 || s.indexOf("black box") > -1 || s.indexOf("white box") > -1 ||
        s.indexOf("एल्गो") > -1 || s.indexOf("அல்கோ") > -1) return "algo";
    if (s.indexOf("stock") > -1 || s.indexOf("price") > -1 || s.indexOf("share") > -1 ||
        s.indexOf("result") > -1 || s.indexOf("p/e") > -1 || s.indexOf("स्टॉक") > -1 ||
        s.indexOf("பங்கு") > -1) return "stock";
    return "generic";
  }

  function bubble(role, text) {
    var b = document.createElement("div");
    b.className = "bubble " + role;
    b.textContent = text;
    return b;
  }
  function citeChip(srcText) {
    var c = document.createElement("a");
    c.className = "cite"; c.href = "#";
    c.innerHTML = '<i class="ti ti-file-text" aria-hidden="true"></i><span></span>';
    c.querySelector("span").textContent = t("src_prefix") + ": " + srcText;
    c.addEventListener("click", function (e) { e.preventDefault(); });
    return c;
  }

  var assistBody;
  function botReply(text) {
    var kind = classify(text);
    var typing = document.createElement("div");
    typing.className = "typing"; typing.textContent = "…";
    assistBody.appendChild(typing);
    assistBody.scrollTop = assistBody.scrollHeight;
    setTimeout(function () {
      typing.remove();
      if (kind === "generic") {
        assistBody.appendChild(bubble("bot", t("ans_generic")));
      } else {
        assistBody.appendChild(bubble("bot", t("ans_" + kind)));
        assistBody.appendChild(citeChip(t("src_" + kind)));
      }
      var d = document.createElement("div");
      d.className = "disclaimer"; d.setAttribute("data-i18n", "w_disclaimer");
      d.textContent = t("w_disclaimer");
      assistBody.appendChild(d);
      assistBody.scrollTop = assistBody.scrollHeight;
    }, 450);
  }
  function userAsk(text) {
    if (!text) return;
    assistBody.appendChild(bubble("user", text));
    assistBody.scrollTop = assistBody.scrollHeight;
    botReply(text);
  }

  function buildWidget() {
    var launch = document.createElement("button");
    launch.id = "assist-launch";
    launch.setAttribute("aria-label", "Open assistant");
    launch.innerHTML = '<i class="ti ti-message-chatbot" aria-hidden="true"></i>';

    var panel = document.createElement("div");
    panel.id = "assist-panel";
    panel.setAttribute("role", "dialog");
    panel.setAttribute("aria-label", "Assistant");

    var head = document.createElement("div");
    head.className = "assist-head";
    head.innerHTML = '<span class="t" data-i18n="w_title"></span>';
    var acts = document.createElement("div"); acts.className = "acts";
    acts.appendChild(langSwitcher());
    var fs = document.createElement("button"); fs.setAttribute("aria-label", t("w_fullscreen"));
    fs.innerHTML = '<i class="ti ti-arrows-maximize" aria-hidden="true"></i>';
    fs.addEventListener("click", function () { panel.classList.toggle("fullscreen"); });
    var close = document.createElement("button"); close.setAttribute("aria-label", t("w_close"));
    close.innerHTML = '<i class="ti ti-x" aria-hidden="true"></i>';
    close.addEventListener("click", function () { panel.classList.remove("open"); launch.focus(); });
    acts.appendChild(fs); acts.appendChild(close);
    head.appendChild(acts);

    assistBody = document.createElement("div");
    assistBody.className = "assist-body";
    assistBody.setAttribute("aria-live", "polite");
    var greet = bubble("bot", t("w_greet"));
    greet.setAttribute("data-i18n", "w_greet");
    assistBody.appendChild(greet);

    var foot = document.createElement("div");
    foot.className = "assist-foot";
    var input = document.createElement("input");
    input.type = "text"; input.setAttribute("data-i18n-ph", "w_input_ph");
    input.setAttribute("aria-label", "Message"); input.placeholder = t("w_input_ph");
    var send = document.createElement("button");
    send.setAttribute("aria-label", t("w_send"));
    send.innerHTML = '<i class="ti ti-arrow-up" aria-hidden="true"></i>';
    function submit() { var v = input.value.trim(); if (v) { userAsk(v); input.value = ""; } }
    send.addEventListener("click", submit);
    input.addEventListener("keydown", function (e) { if (e.key === "Enter") submit(); });
    foot.appendChild(input); foot.appendChild(send);

    var human = document.createElement("div");
    human.className = "assist-human";
    human.innerHTML = '<a href="#" data-i18n="w_human"></a>';
    human.querySelector("a").addEventListener("click", function (e) {
      e.preventDefault();
      assistBody.appendChild(bubble("bot", t("w_human") + " — " + t("contact_lead")));
      assistBody.scrollTop = assistBody.scrollHeight;
    });

    panel.appendChild(head);
    panel.appendChild(assistBody);
    panel.appendChild(foot);
    panel.appendChild(human);

    launch.addEventListener("click", function () {
      panel.classList.toggle("open");
      if (panel.classList.contains("open")) {
        if (window.ASSIST_SEED && !panel.dataset.seeded) {
          input.value = window.ASSIST_SEED; panel.dataset.seeded = "1";
        }
        input.focus();
      }
    });

    document.body.appendChild(launch);
    document.body.appendChild(panel);
    window.BA_ask = userAsk;
  }

  function init() {
    try { state.lang = localStorage.getItem("ba_lang") || "en"; } catch (e) {}
    buildHeader();
    buildFooter();
    buildWidget();
    applyLang(state.lang);
    document.querySelectorAll("[data-ask]").forEach(function (el) {
      el.addEventListener("click", function (e) {
        e.preventDefault();
        document.getElementById("assist-launch").click();
        window.BA_ask(t(el.getAttribute("data-ask")));
      });
    });
    var form = document.getElementById("contact-form");
    if (form) {
      form.addEventListener("submit", function (e) {
        e.preventDefault();
        var ok = document.getElementById("contact-success");
        if (ok) { ok.hidden = false; ok.textContent = t("contact_success"); ok.focus(); }
        form.reset();
      });
    }
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
})();

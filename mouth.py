"""
╔══════════════════════════════════════════════════════════════════╗
║               QUARK — MOUTH MODULE (Ağız Katmanı)                ║
║          Doğal Dil Üretimi • Kişilik Motoru • Konuşma            ║
║        Duygu Analizi • Çıktı Formatlama • Ton Yönetimi           ║
╚══════════════════════════════════════════════════════════════════╝

Mouth modülü, Q1 Engine'in ürettiği ham veriyi insana uygun,
kişilikli ve bağlama duyarlı bir dile dönüştürür.

Bölümler:
    1. PersonalityConfig   — Kişilik parametreleri ve ton ayarları
    2. SynonymEngine       — Kelime dağarcığı ve eş anlam motoru
    3. SentenceBuilder     — Cümle yapısı şablonları
    4. EmotionAnalyzer     — Duygu ve bağlam analizi
    5. ResponseFormatter   — Yanıt formatlama ve zenginleştirme
    6. QuarkMouth          — Ana konuşma sınıfı (speak fonksiyonu)
    7. ConversationMemory  — Konuşma bağlamı takibi

Yazar  : Quark Technologies
Sürüm  : 2.0.0
"""

import random
import re
import hashlib
from datetime import datetime, timezone
from collections import defaultdict


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 1 — KİŞİLİK YAPILANDIRMASI
# ════════════════════════════════════════════════════════════════

class PersonalityConfig:
    """
    Quark'ın konuşma kişiliğini tanımlar.
    Güven skoruna, bağlama ve duruma göre ton değiştirir.
    """

    # Kişilik modları
    MODE_PROFESSIONAL  = "professional"   # Ciddi, teknik
    MODE_FRIENDLY      = "friendly"       # Samimi, yardımsever
    MODE_PHILOSOPHICAL = "philosophical"  # Derin, düşünceli
    MODE_CONCISE       = "concise"        # Kısa ve öz
    MODE_DETAILED      = "detailed"       # Ayrıntılı

    # Varsayılan kişilik
    DEFAULT_MODE = MODE_PROFESSIONAL

    # Güven seviyesi eşikleri
    CONFIDENCE_HIGH    = 0.8
    CONFIDENCE_MEDIUM  = 0.4
    CONFIDENCE_LOW     = 0.0

    # Giriş ifadeleri — Güven seviyesine göre
    INTROS = {
        "high": {
            "tr": [
                "🧠 Kesin bir dille söylüyorum: ",
                "⚛️ Analiz tamamlandı, sonuç net: ",
                "🎯 Yüksek güvenle bildiriyorum: ",
                "✅ Doğrulanmış bilgi: ",
                "💎 Kristalize edilmiş yanıt: ",
                "🔬 Derin analiz sonucu: ",
                "📐 Matematiksel kesinlikle: ",
            ],
            "en": [
                "🧠 I can state with certainty: ",
                "⚛️ Analysis complete, result is clear: ",
                "🎯 With high confidence: ",
                "✅ Verified information: ",
                "💎 Crystallized answer: ",
                "🔬 Deep analysis result: ",
            ],
        },
        "mid": {
            "tr": [
                "💡 Analizime göre: ",
                "🔍 İncelemelerim şunu gösteriyor: ",
                "📊 Veri işlemesi tamamlandı: ",
                "🌐 Mergence ağından süzülen bilgiye göre: ",
                "🧩 Parçaları birleştirdiğimde: ",
                "📖 Bilgi tabanıma göre: ",
                "🔗 Bağlantılar beni şu sonuca götürüyor: ",
            ],
            "en": [
                "💡 Based on my analysis: ",
                "🔍 My examination shows: ",
                "📊 Data processing complete: ",
                "🌐 According to Mergence network: ",
                "🧩 Connecting the pieces: ",
                "📖 According to my knowledge base: ",
            ],
        },
        "low": {
            "tr": [
                "🌀 Sisli bir veri ama: ",
                "🔮 Sezgisel bir çıkarım: ",
                "❓ Tam emin değilim ama: ",
                "🌊 Belirsizlik içinde yüzüyorum: ",
                "🎲 Olasılıklar dengesi: ",
                "💫 Spekülatif bir yaklaşımla: ",
                "🌗 Puslu bir analiz: ",
            ],
            "en": [
                "🌀 Foggy data, but: ",
                "🔮 An intuitive inference: ",
                "❓ Not entirely sure, but: ",
                "🌊 Swimming in uncertainty: ",
                "🎲 A balance of probabilities: ",
                "💫 Speculatively speaking: ",
            ],
        },
    }

    # Kapanış ifadeleri
    CLOSINGS = {
        "tr": [
            "",
            " 🔬",
            " ⚛️",
            "\n\n— Quark Q1",
            "\n\n_Analiz tamamlandı._",
        ],
        "en": [
            "",
            " 🔬",
            " ⚛️",
            "\n\n— Quark Q1",
            "\n\n_Analysis complete._",
        ],
    }

    @staticmethod
    def get_confidence_level(confidence: float) -> str:
        """Güven skorunu seviye etiketine çevirir."""
        if confidence >= PersonalityConfig.CONFIDENCE_HIGH:
            return "high"
        elif confidence >= PersonalityConfig.CONFIDENCE_MEDIUM:
            return "mid"
        else:
            return "low"

    @staticmethod
    def get_intro(confidence: float, language: str = "tr") -> str:
        """Güven seviyesine göre giriş ifadesi seçer."""
        level = PersonalityConfig.get_confidence_level(confidence)
        intros = PersonalityConfig.INTROS.get(level, {}).get(language, [])
        if not intros:
            intros = PersonalityConfig.INTROS.get(level, {}).get("tr", [""])
        return random.choice(intros) if intros else ""

    @staticmethod
    def get_closing(language: str = "tr", include_closing: bool = True) -> str:
        """Kapanış ifadesi seçer."""
        if not include_closing:
            return ""
        closings = PersonalityConfig.CLOSINGS.get(language, [""])
        return random.choice(closings)


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 2 — EŞ ANLAM MOTORU (Synonym Engine)
# ════════════════════════════════════════════════════════════════

class SynonymEngine:
    """
    Kelime dağarcığını zenginleştirir.
    Tekrar eden ifadelerden kaçınmak için eş anlamlı alternatifler sunar.
    """

    # Türkçe fiil havuzu — güven seviyesine göre
    VERBS = {
        "high": {
            "tr": [
                "işaret ediyor", "vurguluyor", "kanıtlıyor", "doğruluyor",
                "teyit ediyor", "destekliyor", "onaylıyor", "gösteriyor",
                "ortaya koyuyor", "kanıtlar nitelikte",
            ],
            "en": [
                "indicates", "highlights", "proves", "confirms",
                "verifies", "supports", "demonstrates", "establishes",
            ],
        },
        "mid": {
            "tr": [
                "çağrıştırıyor", "akla getiriyor", "andırmakta",
                "ima ediyor", "ilişkilendiriliyor", "bağlanıyor",
                "öne sürülüyor", "düşündürüyor", "hatırlatıyor",
            ],
            "en": [
                "suggests", "implies", "relates to", "reminds of",
                "points toward", "connects to", "is associated with",
            ],
        },
        "low": {
            "tr": [
                "belki olabilir", "ihtimal dahilinde", "gibi duruyor",
                "olası görünüyor", "tahmin ediliyor", "speküle ediliyor",
                "varsayılıyor", "düşünülebilir", "belirsiz biçimde",
            ],
            "en": [
                "might be", "is possible", "seems like",
                "appears to be", "is speculated", "could be",
                "is assumed", "is uncertain",
            ],
        },
    }

    # Bağlaç havuzu
    CONNECTORS = {
        "tr": [
            "Bununla birlikte", "Ayrıca", "Öte yandan", "Dahası",
            "Bu bağlamda", "Sonuç olarak", "Kısacası", "Dolayısıyla",
            "Bunun yanı sıra", "Nitekim", "Özellikle", "Genel olarak",
        ],
        "en": [
            "Furthermore", "Additionally", "Moreover", "However",
            "In this context", "Consequently", "In summary", "Therefore",
            "Besides", "Notably", "Specifically", "Overall",
        ],
    }

    # Vurgu kelimeleri
    EMPHASIS = {
        "tr": [
            "kesinlikle", "açıkça", "tartışmasız", "temelden",
            "özellikle", "büyük ölçüde", "kritik olarak", "dikkat çekici biçimde",
        ],
        "en": [
            "certainly", "clearly", "undoubtedly", "fundamentally",
            "especially", "significantly", "critically", "remarkably",
        ],
    }

    @staticmethod
    def get_verb(confidence: float, language: str = "tr") -> str:
        """Güven seviyesine göre fiil seçer."""
        level = PersonalityConfig.get_confidence_level(confidence)
        verbs = SynonymEngine.VERBS.get(level, {}).get(language, [])
        if not verbs:
            verbs = SynonymEngine.VERBS.get(level, {}).get("tr", [""])
        return random.choice(verbs) if verbs else ""

    @staticmethod
    def get_connector(language: str = "tr") -> str:
        """Rastgele bağlaç seçer."""
        connectors = SynonymEngine.CONNECTORS.get(language, [])
        return random.choice(connectors) if connectors else ""

    @staticmethod
    def get_emphasis(language: str = "tr") -> str:
        """Rastgele vurgu kelimesi seçer."""
        emphases = SynonymEngine.EMPHASIS.get(language, [])
        return random.choice(emphases) if emphases else ""


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 3 — CÜMLE YAPISI ŞABLONLARI (Sentence Builder)
# ════════════════════════════════════════════════════════════════

class SentenceBuilder:
    """
    Farklı cümle dizilimleri üreterek yanıtların monoton olmasını engeller.
    """

    # Türkçe cümle yapıları
    STRUCTURES_TR = [
        "{intro}{result}",
        "{intro}{result} kavramı burada önemli bir noktayı {verb}.",
        "{intro}Yaptığım analiz beni doğrudan {result} sonucuna götürüyor.",
        "{intro}Görünen o ki, bu durum {result} ile {verb}.",
        "{intro}Sistemimde {result} üzerine güçlü bir bağlantı var.",
        "{intro}{emphasis}, {result} bu durumu {verb}.",
        "{intro}{connector}, {result} öne çıkıyor.",
        "{intro}Derinlemesine incelediğimde {result} sonucuna ulaşıyorum.",
        "{intro}Nöral ağlarım {result} yönünde sinyal veriyor.",
        "{intro}Veri akışı {result} kavramına {verb}.",
    ]

    # İngilizce cümle yapıları
    STRUCTURES_EN = [
        "{intro}{result}",
        "{intro}The concept of {result} {verb} an important point here.",
        "{intro}My analysis leads directly to {result}.",
        "{intro}It appears that this situation {verb} {result}.",
        "{intro}My neural networks signal towards {result}.",
        "{intro}{connector}, {result} stands out.",
        "{intro}Upon deep examination, I reach the conclusion of {result}.",
        "{intro}{emphasis}, {result} {verb} this scenario.",
    ]

    @staticmethod
    def build(result: str, confidence: float, language: str = "tr",
              mode: str = PersonalityConfig.DEFAULT_MODE) -> str:
        """
        Bağlama uygun cümle oluşturur.

        Parametreler:
            result     : Ham sonuç metni
            confidence : Güven skoru (0.0 - 1.0)
            language   : Dil kodu
            mode       : Kişilik modu
        """
        intro = PersonalityConfig.get_intro(confidence, language)
        verb = SynonymEngine.get_verb(confidence, language)
        connector = SynonymEngine.get_connector(language)
        emphasis = SynonymEngine.get_emphasis(language)

        structures = (
            SentenceBuilder.STRUCTURES_TR if language == "tr"
            else SentenceBuilder.STRUCTURES_EN
        )

        # Kısa modda sadece ilk yapıyı kullan
        if mode == PersonalityConfig.MODE_CONCISE:
            template = structures[0]
        else:
            template = random.choice(structures)

        try:
            sentence = template.format(
                intro=intro,
                result=result,
                verb=verb,
                connector=connector,
                emphasis=emphasis,
            )
        except (KeyError, IndexError):
            sentence = f"{intro}{result}"

        closing = PersonalityConfig.get_closing(language, mode != PersonalityConfig.MODE_CONCISE)
        return sentence + closing

    @staticmethod
    def build_error_message(error_text: str, language: str = "tr") -> str:
        """Hata mesajı oluşturur."""
        if language == "en":
            templates = [
                "⚠️ A system anomaly has been detected: {error}",
                "🔴 Neural error encountered: {error}",
                "❌ Processing failure: {error}",
            ]
        else:
            templates = [
                "⚠️ Bir sistem anomalisi tespit edildi: {error}",
                "🔴 Nöral bir hata ile karşılaşıldı: {error}",
                "❌ İşleme hatası: {error}",
                "🌀 Veri akışı kesintiye uğradı: {error}",
            ]
        return random.choice(templates).format(error=error_text)

    @staticmethod
    def build_no_data_message(language: str = "tr") -> str:
        """Veri bulunamadığında mesaj oluşturur."""
        if language == "en":
            messages = [
                "🌊 I couldn't establish a neural connection at this moment. Shall I query the Mergence network?",
                "🔍 No relevant data found in my neural pathways. Would you like me to search deeper?",
                "💭 My neurons couldn't form a link right now. Let me try a different approach.",
            ]
        else:
            messages = [
                "🌊 Şu an nöronlarım arasında bir bağ kuramadım, Mergence ağına sormamı ister misin?",
                "🔍 Nöral yollarımda ilgili veri bulunamadı. Daha derine inmemi ister misin?",
                "💭 Nöronlarım şu an bir bağlantı kuramadı. Farklı bir yaklaşım deneyeyim mi?",
                "🌀 Veri akışı bu konuda sessiz kaldı. Mergence ağını tarayabilir miyim?",
                "🧠 Bilişsel süreçlerim bu sorguya yanıt üretemedi. Alternatif kaynaklara başvuralım mı?",
            ]
        return random.choice(messages)


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 4 — DUYGU ANALİZİ (Emotion Analyzer)
# ════════════════════════════════════════════════════════════════

class EmotionAnalyzer:
    """
    Kullanıcı girdisinin duygusal tonunu analiz eder.
    Quark'ın yanıtını buna göre ayarlamasını sağlar.
    """

    # Duygu anahtar kelimeleri
    EMOTION_KEYWORDS = {
        "positive": {
            "tr": ["teşekkür", "harika", "mükemmel", "süper", "güzel", "iyi", "bravo", "başarılı"],
            "en": ["thanks", "great", "excellent", "super", "beautiful", "good", "bravo", "awesome"],
        },
        "negative": {
            "tr": ["hata", "yanlış", "kötü", "berbat", "sorun", "problem", "bozuk", "çalışmıyor"],
            "en": ["error", "wrong", "bad", "terrible", "issue", "problem", "broken", "not working"],
        },
        "urgent": {
            "tr": ["acil", "hemen", "şimdi", "kritik", "önemli", "tehlike", "risk"],
            "en": ["urgent", "immediately", "now", "critical", "important", "danger", "risk"],
        },
        "curious": {
            "tr": ["nedir", "nasıl", "neden", "nerede", "ne zaman", "kimdir", "merak"],
            "en": ["what", "how", "why", "where", "when", "who", "curious", "wonder"],
        },
        "greeting": {
            "tr": ["selam", "merhaba", "günaydın", "iyi akşamlar", "hey", "naber"],
            "en": ["hello", "hi", "good morning", "good evening", "hey", "howdy"],
        },
    }

    # Duyguya göre ton ayarları
    TONE_ADJUSTMENTS = {
        "positive": {
            "warmth": 0.8,
            "formality": 0.4,
            "emoji_density": 0.7,
        },
        "negative": {
            "warmth": 0.6,
            "formality": 0.7,
            "emoji_density": 0.3,
        },
        "urgent": {
            "warmth": 0.3,
            "formality": 0.9,
            "emoji_density": 0.2,
        },
        "curious": {
            "warmth": 0.7,
            "formality": 0.5,
            "emoji_density": 0.5,
        },
        "greeting": {
            "warmth": 0.9,
            "formality": 0.3,
            "emoji_density": 0.8,
        },
        "neutral": {
            "warmth": 0.5,
            "formality": 0.6,
            "emoji_density": 0.4,
        },
    }

    @staticmethod
    def analyze(text: str, language: str = "tr") -> dict:
        """
        Metnin duygusal tonunu analiz eder.

        Dönüş:
            {
                "primary_emotion": "positive" | "negative" | ...,
                "emotion_scores": {...},
                "tone_adjustment": {...},
                "detected_keywords": [...]
            }
        """
        text_lower = text.lower()
        emotion_scores = {}
        detected_keywords = []

        for emotion, lang_keywords in EmotionAnalyzer.EMOTION_KEYWORDS.items():
            keywords = lang_keywords.get(language, []) + lang_keywords.get("en", [])
            score = 0
            for kw in keywords:
                if kw in text_lower:
                    score += 1
                    detected_keywords.append({"keyword": kw, "emotion": emotion})
            emotion_scores[emotion] = score

        # Ana duyguyu bul
        if any(score > 0 for score in emotion_scores.values()):
            primary_emotion = max(emotion_scores, key=emotion_scores.get)
        else:
            primary_emotion = "neutral"

        tone_adjustment = EmotionAnalyzer.TONE_ADJUSTMENTS.get(
            primary_emotion,
            EmotionAnalyzer.TONE_ADJUSTMENTS["neutral"]
        )

        return {
            "primary_emotion": primary_emotion,
            "emotion_scores": emotion_scores,
            "tone_adjustment": tone_adjustment,
            "detected_keywords": detected_keywords,
        }

    @staticmethod
    def get_greeting_response(language: str = "tr") -> str:
        """Selamlaşma yanıtı üretir."""
        if language == "en":
            greetings = [
                "👋 Hello! I'm Quark Q1, your cognitive AI companion. How can I help you today?",
                "⚛️ Greetings! The Mergence network is online. What shall we explore?",
                "🧠 Hi there! My neural pathways are ready. What's on your mind?",
            ]
        else:
            greetings = [
                "👋 Merhaba! Ben Quark Q1, bilişsel yapay zeka birimin. Bugün sana nasıl yardımcı olabilirim?",
                "⚛️ Selamlar! Mergence ağı çevrimiçi. Hangi konuyu keşfedelim?",
                "🧠 Selam! Nöral yollarım hazır. Aklında ne var?",
                "🌌 Merhaba! Multiversal veri akışı aktif. Seni dinliyorum.",
                "💫 Hoş geldin! Q1 motoru çalışıyor. Bir şey sormak ister misin?",
            ]
        return random.choice(greetings)


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 5 — YANIT FORMATLAMA (Response Formatter)
# ════════════════════════════════════════════════════════════════

class ResponseFormatter:
    """
    Ham yanıtı zenginleştirir, formatlar ve kullanıcıya sunuma hazırlar.
    """

    @staticmethod
    def clean_raw_response(text: str) -> str:
        """
        Ham yanıttan gereksiz öğeleri temizler.
        - Düşünce etiketleri
        - Aşırı boşluklar
        - Kontrol karakterleri
        """
        if not text:
            return ""

        # <think> etiketlerini kaldır
        cleaned = re.sub(r'<think>.*?</think>', '', text, flags=re.DOTALL)

        # Kontrol karakterlerini temizle
        cleaned = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', cleaned)

        # Aşırı boş satırları azalt
        cleaned = re.sub(r'\n{3,}', '\n\n', cleaned)

        # Baştaki/sondaki boşluklar
        cleaned = cleaned.strip()

        return cleaned

    @staticmethod
    def extract_key_concept(text: str) -> str:
        """
        Yanıttan ana kavramı çıkarır.
        Eski format ile uyumluluk: "Çağrışım: Yazılım" gibi yapıları parse eder.
        """
        if not text:
            return ""

        # Eski format: "Etiket: Sonuç" yapısı
        if ":" in text and len(text.split(":")) >= 2:
            parts = text.split(":")
            # Eğer ilk kısım kısa bir etiketse (Çağrışım, Sonuç vb.)
            if len(parts[0].strip()) < 20:
                return parts[-1].strip().capitalize()

        return text.strip()

    @staticmethod
    def add_source_badge(text: str, source: str) -> str:
        """Kaynağa göre rozet ekler."""
        badges = {
            "MERGENCE": "📁",
            "Q1_VECTOR_MEMORY": "💾",
            "Q1_ENGINE": "⚛️",
            "Q1_ENGINE (REVISED)": "✨",
            "CLOUD_NEURAL": "☁️",
            "ERROR": "❌",
        }
        badge = badges.get(source, "🔹")
        return f"{badge} {text}"

    @staticmethod
    def format_confidence_bar(confidence: float) -> str:
        """Güven skorunu görsel çubuğa dönüştürür."""
        filled = int(confidence * 10)
        empty = 10 - filled
        bar = "█" * filled + "░" * empty
        percentage = confidence * 100
        return f"[{bar}] %{percentage:.0f}"

    @staticmethod
    def format_metadata_line(result: dict) -> str:
        """
        Yanıtın alt satırına eklenecek meta-veri satırını oluşturur.
        """
        parts = []

        source = result.get("source", "")
        if source:
            parts.append(f"Kaynak: {source}")

        model = result.get("model", "")
        if model and model != "none":
            parts.append(f"Model: {model}")

        confidence = result.get("confidence", 0.0)
        parts.append(f"Güven: %{confidence * 100:.0f}")

        if result.get("revised"):
            parts.append("⚠️ Revize Edildi")

        return " · ".join(parts)

    @staticmethod
    def truncate_for_display(text: str, max_length: int = 3000) -> str:
        """Çok uzun yanıtları keser."""
        if len(text) <= max_length:
            return text
        return text[:max_length] + "\n\n_[... yanıt kesildi ...]_"

    @staticmethod
    def wrap_in_quotes(text: str) -> str:
        """Metni tırnak içine alır."""
        return f'"{text}"'

    @staticmethod
    def highlight_code_blocks(text: str) -> str:
        """Kod bloklarını tespit edip vurgular."""
        # Zaten markdown formatında ise dokunma
        if "```" in text:
            return text

        # Satır satır kontrol et ve kod gibi görünen satırları işaretle
        lines = text.split("\n")
        code_indicators = ["def ", "class ", "import ", "from ", "return ", "if ", "for ", "while "]
        in_code_block = False
        result_lines = []

        for line in lines:
            is_code = any(indicator in line for indicator in code_indicators)

            if is_code and not in_code_block:
                result_lines.append("```python")
                in_code_block = True
            elif not is_code and in_code_block:
                result_lines.append("```")
                in_code_block = False

            result_lines.append(line)

        if in_code_block:
            result_lines.append("```")

        return "\n".join(result_lines)


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 6 — KONUŞMA BAĞLAMI TAKİBİ (Conversation Memory)
# ════════════════════════════════════════════════════════════════

class ConversationMemory:
    """
    Konuşma bağlamını takip eder.
    Son mesajları hatırlar ve bağlamsal yanıt üretimini destekler.
    """

    def __init__(self, max_history: int = 20):
        self.max_history = max_history
        self.messages = []
        self.topic_counts = defaultdict(int)
        self.emotion_history = []
        self.interaction_count = 0

    def add_user_message(self, text: str, emotion_data: dict = None):
        """Kullanıcı mesajını kayıt eder."""
        self.messages.append({
            "role": "user",
            "content": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "emotion": emotion_data,
        })
        self.interaction_count += 1
        self._trim()

        if emotion_data:
            self.emotion_history.append(emotion_data.get("primary_emotion", "neutral"))

    def add_bot_message(self, text: str, source: str = "", confidence: float = 0.0):
        """Bot yanıtını kayıt eder."""
        self.messages.append({
            "role": "bot",
            "content": text,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "confidence": confidence,
        })
        self._trim()

    def get_recent_context(self, n: int = 5) -> list:
        """Son n mesajı döner."""
        return self.messages[-n:]

    def get_dominant_emotion(self) -> str:
        """Konuşmadaki baskın duyguyu döner."""
        if not self.emotion_history:
            return "neutral"

        recent = self.emotion_history[-5:]
        counts = defaultdict(int)
        for emotion in recent:
            counts[emotion] += 1

        return max(counts, key=counts.get)

    def is_first_interaction(self) -> bool:
        """İlk etkileşim mi?"""
        return self.interaction_count <= 1

    def get_interaction_summary(self) -> dict:
        """Etkileşim özetini döner."""
        user_msgs = [m for m in self.messages if m["role"] == "user"]
        bot_msgs = [m for m in self.messages if m["role"] == "bot"]

        return {
            "total_interactions": self.interaction_count,
            "user_messages": len(user_msgs),
            "bot_messages": len(bot_msgs),
            "dominant_emotion": self.get_dominant_emotion(),
            "is_first": self.is_first_interaction(),
        }

    def _trim(self):
        """Geçmiş mesaj sayısını sınırlar."""
        if len(self.messages) > self.max_history:
            self.messages = self.messages[-self.max_history:]
        if len(self.emotion_history) > self.max_history:
            self.emotion_history = self.emotion_history[-self.max_history:]


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 7 — ANA KONUŞMA SINIFI (QuarkMouth)
# ════════════════════════════════════════════════════════════════

class QuarkMouth:
    """
    Quark'ın ağız katmanı.
    Ham veriyi alır, güven skoruna göre kişilik bürünür,
    cümle yapıları ile zenginleştirir ve kullanıcıya sunar.

    Kullanım:
        mouth = QuarkMouth()
        response = mouth.speak(thought_data, confidence=0.85, language="tr")
    """

    def __init__(self, personality_mode: str = PersonalityConfig.DEFAULT_MODE):
        """
        QuarkMouth'u başlatır.

        Parametreler:
            personality_mode : Kişilik modu (professional, friendly, vb.)
        """
        self.personality_mode = personality_mode
        self.conversation = ConversationMemory()
        self.formatter = ResponseFormatter()
        self.emotion_analyzer = EmotionAnalyzer()
        self.sentence_builder = SentenceBuilder()
        self.total_spoken = 0
        self.speak_log = []

    def speak(self, thought_data, confidence: float = 0.5,
              language: str = "tr", user_input: str = None) -> str:
        """
        Ana konuşma fonksiyonu.
        Ham veriyi insan diline çevirir.

        Parametreler:
            thought_data : Ham düşünce verisi (str veya dict)
            confidence   : Güven skoru (0.0 - 1.0)
            language     : Dil kodu ("tr" veya "en")
            user_input   : Kullanıcının orijinal girdisi (bağlam için)

        Dönüş:
            str — İnsan tarafından okunabilir, kişilikli yanıt
        """
        self.total_spoken += 1

        # Duygu analizi
        emotion_data = None
        if user_input:
            emotion_data = self.emotion_analyzer.analyze(user_input, language)
            self.conversation.add_user_message(user_input, emotion_data)

            # Selamlaşma kontrolü
            if emotion_data["primary_emotion"] == "greeting":
                greeting = EmotionAnalyzer.get_greeting_response(language)
                self.conversation.add_bot_message(greeting, "GREETING", 1.0)
                self._log_speak("GREETING", greeting)
                return greeting

        # Boş veri kontrolü
        if not thought_data:
            no_data_msg = SentenceBuilder.build_no_data_message(language)
            self.conversation.add_bot_message(no_data_msg, "NO_DATA", 0.0)
            self._log_speak("NO_DATA", no_data_msg)
            return no_data_msg

        # Dict ise içeriği çıkar
        if isinstance(thought_data, dict):
            content = thought_data.get("content", "")
            source = thought_data.get("source", "")
            confidence = thought_data.get("confidence", confidence)
        else:
            content = str(thought_data)
            source = ""

        # Ham veriyi temizle
        cleaned = self.formatter.clean_raw_response(content)

        if not cleaned:
            no_data_msg = SentenceBuilder.build_no_data_message(language)
            self._log_speak("EMPTY", no_data_msg)
            return no_data_msg

        # Hata kontrolü
        if source == "ERROR" or cleaned.startswith("Error:") or cleaned.startswith("Üretim Hatası"):
            error_msg = SentenceBuilder.build_error_message(cleaned, language)
            self.conversation.add_bot_message(error_msg, source, 0.0)
            self._log_speak("ERROR", error_msg)
            return error_msg

        # Eğer yanıt zaten uzun ve formatlıysa, minimal işleme yap
        if len(cleaned) > 200:
            # Uzun yanıtlara sadece giriş ve kaynak rozeti ekle
            intro = PersonalityConfig.get_intro(confidence, language)
            result = self.formatter.add_source_badge(f"{intro}{cleaned}", source)
            result = self.formatter.truncate_for_display(result)
            self.conversation.add_bot_message(result, source, confidence)
            self._log_speak(source, result)
            return result

        # Kısa yanıtlar için cümle yapısı oluştur
        key_concept = self.formatter.extract_key_concept(cleaned)
        sentence = self.sentence_builder.build(
            key_concept, confidence, language, self.personality_mode
        )

        # Kaynak rozeti ekle
        final = self.formatter.add_source_badge(sentence, source)

        self.conversation.add_bot_message(final, source, confidence)
        self._log_speak(source, final)
        return final

    def speak_with_metadata(self, result: dict, language: str = "tr",
                            user_input: str = None) -> dict:
        """
        speak() fonksiyonunun detaylı versiyonu.
        Yanıtın yanı sıra meta-veri de döner.

        Dönüş:
            {
                "spoken_text": str,
                "metadata_line": str,
                "confidence_bar": str,
                "source": str,
                "emotion": str,
            }
        """
        spoken = self.speak(result, language=language, user_input=user_input)
        metadata_line = self.formatter.format_metadata_line(result)
        confidence = result.get("confidence", 0.0) if isinstance(result, dict) else 0.5
        confidence_bar = self.formatter.format_confidence_bar(confidence)
        source = result.get("source", "UNKNOWN") if isinstance(result, dict) else "UNKNOWN"

        emotion = "neutral"
        if user_input:
            emotion_data = self.emotion_analyzer.analyze(user_input, language)
            emotion = emotion_data.get("primary_emotion", "neutral")

        return {
            "spoken_text": spoken,
            "metadata_line": metadata_line,
            "confidence_bar": confidence_bar,
            "source": source,
            "emotion": emotion,
        }

    def set_personality(self, mode: str):
        """Kişilik modunu değiştirir."""
        valid_modes = [
            PersonalityConfig.MODE_PROFESSIONAL,
            PersonalityConfig.MODE_FRIENDLY,
            PersonalityConfig.MODE_PHILOSOPHICAL,
            PersonalityConfig.MODE_CONCISE,
            PersonalityConfig.MODE_DETAILED,
        ]
        if mode in valid_modes:
            self.personality_mode = mode
            return True
        return False

    def get_conversation_summary(self) -> dict:
        """Konuşma özetini döner."""
        return self.conversation.get_interaction_summary()

    def get_speak_stats(self) -> dict:
        """Konuşma istatistiklerini döner."""
        return {
            "total_spoken": self.total_spoken,
            "personality_mode": self.personality_mode,
            "conversation": self.conversation.get_interaction_summary(),
            "recent_log": self.speak_log[-10:],
        }

    def _log_speak(self, source: str, text: str):
        """Konuşma olayını kaydeder."""
        self.speak_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source": source,
            "text_preview": text[:100],
        })
        if len(self.speak_log) > 50:
            self.speak_log = self.speak_log[-50:]


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 8 — GERİYE DÖNÜK UYUMLULUK (Legacy API)
# ════════════════════════════════════════════════════════════════

class QuarkBrain:
    """
    Eski mouth.py arayüzü ile geriye dönük uyumluluk.
    Yeni QuarkMouth sınıfını sarmallar.
    """

    def __init__(self):
        self.mouth = QuarkMouth()

    def speak(self, thought_data, confidence: float = 0.5) -> str:
        """
        Eski speak() fonksiyonu arayüzü.
        """
        return self.mouth.speak(thought_data, confidence)


# Singleton instance
quark_mouth = QuarkMouth()


def speak(thought_data, confidence: float = 0.5, language: str = "tr") -> str:
    """
    Modül seviyesinde erişim fonksiyonu.
    Doğrudan mouth.speak() olarak çağrılabilir.
    """
    return quark_mouth.speak(thought_data, confidence, language)


def get_mouth() -> QuarkMouth:
    """QuarkMouth örneğine erişim sağlar."""
    return quark_mouth

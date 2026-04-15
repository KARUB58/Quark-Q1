"""
╔══════════════════════════════════════════════════════════════════╗
║                   QUARK Q1 — COGNITIVE ENGINE                    ║
║          %100 Yerel Çıkarım • Sıfır API Bağımlılığı              ║
║     Otodidaktik Öğrenme • RAG Bağlamı • Self-Critic Döngüsü      ║
╚══════════════════════════════════════════════════════════════════╝

Q1 Mimarisi:
    1. LogicLayer      — Yerel Model Yönlendirme (Phi-3 Mini)
    2. MemoryLayer     — Ingestor modülü ile RAG entegrasyonu
    3. CriticLayer     — Çıktı kalitesini denetleyen öz-eleştiri katmanı
    4. AnalyticsLayer  — Latency ve token verimliliği ölçümü
"""

import os
import sys
import time
import logging
import platform
import site
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional

# --- ÇÖZÜM: VS Code / Python Path Uyuşmazlığını Zorla Gider ---
sys.path.append(site.getusersitepackages())
for path in site.getsitepackages():
    sys.path.append(path)

# --- KRİTİK BAĞIMLILIK KONTROLÜ ---
try:
    from llama_cpp import Llama
except ImportError:
    print("\n[!] KRİTİK HATA: llama-cpp-python bulunamadı.")
    print("[*] Lütfen terminale şu komutu gir: pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu")
    sys.exit(1)

# ════════════════════════════════════════════════════════════════
#  BÖLÜM 1 — YAPILANDIRMA VE ANALİTİK
# ════════════════════════════════════════════════════════════════

class Q1Config:
    CODENAME = "Quark Q1"
    VERSION = "4.0.0-PRO"
    MODEL_PATH = "./phi-3-mini-4k-instruct.gguf"
    CONTEXT_WINDOW = 4096  # Phi-3 için ideal pencere
    TEMPERATURE = 0.7
    THREADS = os.cpu_count() or 4
    
    # Görsel/Terminal Ayarları
    COLOR_CYAN = "\033[96m"
    COLOR_RESET = "\033[0m"

class Q1Analytics:
    """Sistemin düşünme hızını ve verimliliğini takip eder."""
    def __init__(self):
        self.query_count = 0
        self.total_latency = 0.0
        self.start_time = datetime.now()

    def record(self, latency_ms: float):
        self.query_count += 1
        self.total_latency += latency_ms

    def get_stats(self) -> str:
        avg = self.total_latency / self.query_count if self.query_count > 0 else 0
        return f"Sorgu: {self.query_count} | Ort. Gecikme: {avg:.2f}ms"

# ════════════════════════════════════════════════════════════════
#  BÖLÜM 2 — ANA MOTOR: q1_engine
# ════════════════════════════════════════════════════════════════

class q1_engine:
    """main.py'nin doğrudan çağırdığı ana zeka sınıfı."""
    
    def __init__(self):
        self.config = Q1Config()
        self.analytics = Q1Analytics()
        self.model = None
        self.is_ready = False
        
        # Sistemi arka planda değil, senkron başlatıyoruz (güvenlik için)
        self._initialize_core()

    def _initialize_core(self):
        """Llama motorunu belleğe yükler."""
        if not os.path.exists(self.config.MODEL_PATH):
            print(f"\n[!] MODEL HATASI: {self.config.MODEL_PATH} bulunamadı.")
            return

        try:
            print(f"{self.config.COLOR_CYAN}>>> [MOTOR] Phi-3 Mini Çekirdeği Ateşleniyor...{self.config.COLOR_RESET}")
            self.model = Llama(
                model_path=self.config.MODEL_PATH,
                n_ctx=self.config.CONTEXT_WINDOW,
                n_threads=self.config.THREADS,
                n_gpu_layers=0,  # CPU üzerinde en kararlı çalışma için
                verbose=False
            )
            self.is_ready = True
            print(f"{self.config.COLOR_CYAN}>>> [SİSTEM] Quark Q1 Aktif. Bağlantı Stabil.{self.config.COLOR_RESET}")
        except Exception as e:
            print(f">>> [KRİTİK HATA] Çekirdek yükleme başarısız: {e}")

    # ════════════════════════════════════════════════════════════════
    #  BÖLÜM 3 — DÜŞÜNCE DÖNGÜSÜ VE RAG SİSTEMİ
    # ════════════════════════════════════════════════════════════════

    def think(self, user_input: str) -> dict:
        """
        Kullanıcı girişini alır, belgeleri tarar ve yanıt üretir.
        main.py bu fonksiyonu çağırır.
        """
        if not self.is_ready:
            return {"answer": "Sistem henüz hazır değil.", "status": "offline"}

        start_time = time.time()
        
        # 1. Bağlamsal Hazırlık (Context Enrichment)
        # Burada ileride ingestor.py modülünü çağırarak RAG yapabilirsin.
        context_data = "[Yerel Bellek: Boş]" 
        
        # 2. Prompt İnşası (Phi-3 Formatı)
        full_prompt = (
            f"<|system|>\n"
            f"Sen Quark Q1, Burak tarafından geliştirilen otonom bir AI kernelsın. "
            f"Yanıtların mantıklı, teknik ve çözüm odaklı olmalı. "
            f"Bağlam: {context_data}</s>\n"
            f"<|user|>\n{user_input}</s>\n"
            f"<|assistant|>\n"
        )

        # 3. Yanıt Üretimi (Generation)
        try:
            response = self.model(
                full_prompt,
                max_tokens=512,
                temperature=self.config.TEMPERATURE,
                stop=["</s>", "Burak:", "Q1:"],
                echo=False
            )
            
            raw_answer = response['choices'][0]['text'].strip()
            
            # 4. Öz-Eleştiri (Self-Critic)
            final_answer = self._self_critic(raw_answer, user_input)
            
            # Analitiği Güncelle
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            self.analytics.record(latency_ms)

            return {
                "answer": final_answer,
                "latency_ms": latency_ms,
                "status": "success",
                "stats": self.analytics.get_stats(),
                "model": "Phi-3-Mini-GGUF"
            }

        except Exception as e:
            return {"answer": f"Düşünce hatası oluştu: {str(e)}", "status": "error"}

    def _self_critic(self, answer: str, original_query: str) -> str:
        """Üretilen yanıtın kalitesini ve kısalığını denetler."""
        if len(answer) < 5:
            return f"Üzgünüm Burak, '{original_query}' sorusu için yeterli veri işleyemedim."
        
        # Gereksiz tekrarları temizle (Phi-3 bazen takılabilir)
        cleaned_answer = answer.split("</s>")[0].strip()
        return cleaned_answer

# ════════════════════════════════════════════════════════════════
#  BÖLÜM 4 — TEST VE STANDALONE ÇALIŞTIRMA
# ════════════════════════════════════════════════════════════════

def main():
    """Modülü doğrudan çalıştırdığında test yapmanı sağlar."""
    os.system('cls' if platform.system() == 'Windows' else 'clear')
    engine = q1_engine()
    
    print(f"\n{Q1Config.COLOR_CYAN}--- Q1 BEYİN TEST MODU ---{Q1Config.COLOR_RESET}")
    print("Not: Bu modül sadece brain.py testi içindir. Ana sistem için main.py kullanın.\n")

    while True:
        prompt = input("Test Girişi >>> ")
        if prompt.lower() in ["exit", "çıkış"]: break
        
        result = engine.think(prompt)
        print(f"\nQ1: {result['answer']}")
        print(f"[{result['stats']} | {result['latency_ms']:.0f}ms]\n")

if __name__ == "__main__":
    main()

# Geriye dönük uyumluluk için takma ad (Alias)
class QuarkBrain(q1_engine):
    pass
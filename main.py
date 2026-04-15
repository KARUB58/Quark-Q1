"""
╔══════════════════════════════════════════════════════════════════╗
║               QUARK Q1 — TERMINAL INTERFACE                      ║
║          Renkli İnteraktif Chat • Komut Sistemi                  ║
║          Düşünce Zinciri • Dosya Yutma • Arka Plan İşçisi         ║
╚══════════════════════════════════════════════════════════════════╝

Komutlar:
    /help       — Yardım menüsü
    /status     — Q1 sistem durumu
    /memory     — Hafıza istatistikleri
    /analytics  — Performans analitiği
    /routing    — Model yönlendirme kayıtları
    /think      — Düşünce zinciri göster/gizle
    /ingest     — Dosya yutma (PDF/DOCX/TXT)
    /worker     — Arka plan Hebbian işçisi
    /export     — Sohbet geçmişini dışa aktar
    /clear      — Ekranı temizle
    /quit       — Çıkış

Yazar  : Quark Technologies
Sürüm  : 4.0.0
"""

import os
import sys
import time
import json
from datetime import datetime, timezone


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 1 — ANSI RENK KODLARI
# ════════════════════════════════════════════════════════════════

class Colors:
    """ANSI renk kodları — Terminal güzelleştirmesi."""

    RESET     = "\033[0m"
    BOLD      = "\033[1m"
    DIM       = "\033[2m"
    ITALIC    = "\033[3m"
    UNDERLINE = "\033[4m"

    BLACK     = "\033[30m"
    RED       = "\033[31m"
    GREEN     = "\033[32m"
    YELLOW    = "\033[33m"
    BLUE      = "\033[34m"
    MAGENTA   = "\033[35m"
    CYAN      = "\033[36m"
    WHITE     = "\033[37m"

    BRIGHT_BLACK   = "\033[90m"
    BRIGHT_RED     = "\033[91m"
    BRIGHT_GREEN   = "\033[92m"
    BRIGHT_YELLOW  = "\033[93m"
    BRIGHT_BLUE    = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN    = "\033[96m"
    BRIGHT_WHITE   = "\033[97m"

    BG_BLACK   = "\033[40m"
    BG_RED     = "\033[41m"
    BG_GREEN   = "\033[42m"
    BG_YELLOW  = "\033[43m"
    BG_BLUE    = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN    = "\033[46m"
    BG_WHITE   = "\033[47m"

C = Colors


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 2 — ASCII ART VE BANNER
# ════════════════════════════════════════════════════════════════

QUARK_BANNER = f"""
{C.BRIGHT_CYAN}{C.BOLD}
   ██████╗ ██╗   ██╗ █████╗ ██████╗ ██╗  ██╗
  ██╔═══██╗██║   ██║██╔══██╗██╔══██╗██║ ██╔╝
  ██║   ██║██║   ██║███████║██████╔╝█████╔╝ 
  ██║▄▄ ██║██║   ██║██╔══██║██╔══██╗██╔═██╗ 
  ╚██████╔╝╚██████╔╝██║  ██║██║  ██║██║  ██╗
   ╚══▀▀═╝  ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝
{C.RESET}
  {C.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}
  {C.BRIGHT_WHITE}{C.BOLD}  Q1 Cognitive Engine v4.0 — Fully Local{C.RESET}
  {C.DIM}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{C.RESET}
"""

HELP_TEXT = f"""
{C.BRIGHT_CYAN}{C.BOLD}╔═══════════════════════════════════════════╗
║              Q1 KOMUT MERKEZİ              ║
╚═══════════════════════════════════════════╝{C.RESET}

  {C.BRIGHT_WHITE}{C.BOLD}Sohbet:{C.RESET}
  {C.BRIGHT_GREEN}/help{C.RESET}       {C.DIM}—{C.RESET} Bu yardım menüsünü gösterir
  {C.BRIGHT_GREEN}/think{C.RESET}      {C.DIM}—{C.RESET} Düşünce zinciri göster/gizle
  {C.BRIGHT_GREEN}/clear{C.RESET}      {C.DIM}—{C.RESET} Ekranı temizle
  {C.BRIGHT_GREEN}/export{C.RESET}     {C.DIM}—{C.RESET} Sohbet geçmişini dışa aktar
  {C.BRIGHT_GREEN}/quit{C.RESET}       {C.DIM}—{C.RESET} Çıkış

  {C.BRIGHT_WHITE}{C.BOLD}Sistem:{C.RESET}
  {C.BRIGHT_GREEN}/status{C.RESET}     {C.DIM}—{C.RESET} Q1 Engine sistem durumu
  {C.BRIGHT_GREEN}/memory{C.RESET}     {C.DIM}—{C.RESET} Hafıza (Hebbian) istatistikleri
  {C.BRIGHT_GREEN}/analytics{C.RESET}  {C.DIM}—{C.RESET} Performans analitiği
  {C.BRIGHT_GREEN}/routing{C.RESET}    {C.DIM}—{C.RESET} Model yönlendirme kayıtları

  {C.BRIGHT_WHITE}{C.BOLD}Dosya & Öğrenme:{C.RESET}
  {C.BRIGHT_GREEN}/ingest <dosya>{C.RESET}   {C.DIM}—{C.RESET} Dosya yut (PDF/DOCX/TXT)
  {C.BRIGHT_GREEN}/ingest dir{C.RESET}       {C.DIM}—{C.RESET} ./documents klasörünü tara
  {C.BRIGHT_GREEN}/ingest watch{C.RESET}     {C.DIM}—{C.RESET} Klasör izlemeyi başlat/durdur
  {C.BRIGHT_GREEN}/ingest status{C.RESET}    {C.DIM}—{C.RESET} Yutma istatistikleri
  {C.BRIGHT_GREEN}/worker start{C.RESET}     {C.DIM}—{C.RESET} Hebbian işçiyi başlat
  {C.BRIGHT_GREEN}/worker stop{C.RESET}      {C.DIM}—{C.RESET} Hebbian işçiyi durdur
  {C.BRIGHT_GREEN}/worker status{C.RESET}    {C.DIM}—{C.RESET} İşçi durumu

  {C.DIM}Herhangi bir metin yazarak Q1 ile konuşabilirsiniz.{C.RESET}
"""

GOODBYE_TEXT = f"""
{C.BRIGHT_CYAN}{C.BOLD}
  ╔═══════════════════════════════════════════╗
  ║     Quark Q1 oturumu sonlandırılıyor...   ║
  ╚═══════════════════════════════════════════╝
{C.RESET}
  {C.DIM}Nöral bağlantılar korunuyor...{C.RESET}
  {C.DIM}Deneyimler hafızaya yazılıyor...{C.RESET}
  {C.BRIGHT_CYAN}👋 Görüşmek üzere.{C.RESET}
"""


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 3 — TERMINAL YARDIMCI FONKSİYONLARI
# ════════════════════════════════════════════════════════════════

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_divider(char="━", length=50):
    print(f"  {C.DIM}{char * length}{C.RESET}")

def print_header(text: str):
    print(f"\n  {C.BRIGHT_CYAN}{C.BOLD}{'═' * 45}")
    print(f"  {text}")
    print(f"  {'═' * 45}{C.RESET}\n")

def print_sub_header(text: str):
    print(f"\n  {C.BRIGHT_WHITE}{C.BOLD}── {text} ──{C.RESET}\n")

def print_status_line(label: str, value: str, ok: bool = True):
    icon = f"{C.BRIGHT_GREEN}✅{C.RESET}" if ok else f"{C.BRIGHT_RED}❌{C.RESET}"
    print(f"  {icon} {C.BRIGHT_WHITE}{label}{C.RESET}: {C.CYAN}{value}{C.RESET}")

def print_metric(label: str, value):
    print(f"  {C.DIM}▸{C.RESET} {C.WHITE}{label}{C.RESET}: {C.BRIGHT_YELLOW}{value}{C.RESET}")

def print_metric_bar(label: str, value: float, max_val: float = 100.0, width: int = 20):
    ratio = min(value / max_val, 1.0) if max_val > 0 else 0.0
    filled = int(ratio * width)
    empty = width - filled
    if ratio >= 0.8:
        color = C.BRIGHT_GREEN
    elif ratio >= 0.4:
        color = C.BRIGHT_YELLOW
    else:
        color = C.BRIGHT_RED
    bar = f"{color}{'█' * filled}{C.DIM}{'░' * empty}{C.RESET}"
    print(f"  {C.DIM}▸{C.RESET} {C.WHITE}{label}{C.RESET}: [{bar}] {color}{value:.1f}%{C.RESET}")

def print_user_message(text: str):
    print(f"\n  {C.BRIGHT_BLUE}{C.BOLD}Sen ▸{C.RESET} {C.WHITE}{text}{C.RESET}")

def print_q1_response(text: str):
    print(f"\n  {C.BRIGHT_MAGENTA}{C.BOLD}Q1 ◂{C.RESET}", end=" ")
    lines = text.split("\n")
    for i, line in enumerate(lines):
        if i == 0:
            print(f"{C.BRIGHT_WHITE}{line}{C.RESET}")
        else:
            print(f"       {C.BRIGHT_WHITE}{line}{C.RESET}")

def print_thinking(text: str):
    print(f"\n  {C.BRIGHT_YELLOW}╔{'═' * 43}╗{C.RESET}")
    print(f"  {C.BRIGHT_YELLOW}║{C.RESET}  💭 {C.BOLD}Düşünce Zinciri{C.RESET}                      {C.BRIGHT_YELLOW}║{C.RESET}")
    print(f"  {C.BRIGHT_YELLOW}╠{'═' * 43}╣{C.RESET}")
    for line in text.split("\n"):
        truncated = line[:40]
        padding = 40 - len(truncated)
        print(f"  {C.BRIGHT_YELLOW}║{C.RESET} {C.DIM}{truncated}{' ' * padding}{C.RESET}{C.BRIGHT_YELLOW}║{C.RESET}")
    print(f"  {C.BRIGHT_YELLOW}╚{'═' * 43}╝{C.RESET}")

def print_meta(source: str, model: str, confidence: float,
               elapsed_ms: float, revised: bool, engine: str = ""):
    if confidence >= 0.8:
        conf_color = C.BRIGHT_GREEN
    elif confidence >= 0.4:
        conf_color = C.BRIGHT_YELLOW
    else:
        conf_color = C.BRIGHT_RED
    conf_pct = confidence * 100
    engine_icon = "💻" if engine == "local" else "💾"
    parts = [
        f"{engine_icon} {C.DIM}Kaynak:{C.RESET}{C.CYAN}{source}{C.RESET}",
        f"{C.DIM}Model:{C.RESET}{C.CYAN}{model}{C.RESET}",
        f"{conf_color}%{conf_pct:.0f}{C.RESET}",
        f"{C.DIM}Süre:{C.RESET}{C.CYAN}{elapsed_ms:.0f}ms{C.RESET}",
    ]
    if revised:
        parts.append(f"{C.BRIGHT_YELLOW}⚠ Revize{C.RESET}")
    print(f"  {' · '.join(parts)}")

def print_error(text: str):
    print(f"\n  {C.BRIGHT_RED}{C.BOLD}⚠ HATA:{C.RESET} {C.RED}{text}{C.RESET}")

def print_warning(text: str):
    print(f"  {C.BRIGHT_YELLOW}⚠{C.RESET} {C.YELLOW}{text}{C.RESET}")

def print_info(text: str):
    print(f"  {C.BRIGHT_CYAN}ℹ{C.RESET} {C.WHITE}{text}{C.RESET}")

def print_success(text: str):
    print(f"  {C.BRIGHT_GREEN}✓{C.RESET} {C.GREEN}{text}{C.RESET}")

def format_timestamp(iso_str: str) -> str:
    try:
        dt = datetime.fromisoformat(iso_str)
        return dt.strftime("%H:%M:%S")
    except Exception:
        return iso_str[:19]


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 4 — SOHBET GEÇMİŞİ
# ════════════════════════════════════════════════════════════════

class ChatHistory:
    """Terminal sohbet geçmişini tutar ve dışa aktarır."""

    def __init__(self):
        self.messages = []
        self.session_start = datetime.now(timezone.utc).isoformat()

    def add_user(self, text: str):
        self.messages.append({"role": "user", "content": text, "timestamp": datetime.now(timezone.utc).isoformat()})

    def add_q1(self, text: str, source: str = "", model: str = "",
               confidence: float = 0.0, elapsed_ms: float = 0.0, revised: bool = False):
        self.messages.append({
            "role": "q1", "content": text, "source": source, "model": model,
            "confidence": confidence, "elapsed_ms": round(elapsed_ms, 2),
            "revised": revised, "timestamp": datetime.now(timezone.utc).isoformat(),
        })

    def get_count(self) -> int:
        return len(self.messages)

    def export_json(self, filepath: str = None) -> str:
        if not filepath:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"q1_chat_{ts}.json"
        try:
            export_data = {"session_start": self.session_start, "messages": self.messages}
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(export_data, f, ensure_ascii=False, indent=2)
            return filepath
        except Exception as e:
            return f"HATA: {str(e)}"

    def export_text(self, filepath: str = None) -> str:
        if not filepath:
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = f"q1_chat_{ts}.txt"
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"Quark Q1 Sohbet Geçmişi\n{'=' * 50}\n\n")
                for msg in self.messages:
                    ts_str = format_timestamp(msg.get("timestamp", ""))
                    if msg["role"] == "user":
                        f.write(f"[{ts_str}] Sen: {msg['content']}\n\n")
                    else:
                        f.write(f"[{ts_str}] Q1: {msg['content']}\n\n")
            return filepath
        except Exception as e:
            return f"HATA: {str(e)}"


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 5 — KOMUT İŞLEYİCİLERİ
# ════════════════════════════════════════════════════════════════

def cmd_help():
    print(HELP_TEXT)


def cmd_status(engine):
    status = engine.get_system_status()
    print_header("Q1 ENGINE SİSTEM DURUMU")

    print_sub_header("Genel")
    print_status_line("Versiyon", f"{status['version']} ({status['codename']})")

    local = status.get("local_model", {})
    local_ok = local.get("is_loaded", False)
    print_status_line("Yerel Model", local.get("model_name", "Yüklü Değil"), local_ok)
    if local_ok:
        print_metric("Toplam Çıkarım", local.get("total_inferences", 0))
        print_metric("Üretilen Token", local.get("total_tokens", 0))
    elif local.get("load_error"):
        print_warning(local["load_error"])

    print_sub_header("Vektör Bellek")
    mem = status.get("memory_stats", {})
    print_status_line("ChromaDB", "Aktif" if mem.get("db_ready") else "Pasif", mem.get("db_ready", False))
    print_metric("Deneyim", mem.get("total_memories", 0))

    print_sub_header("RAG (Belge Bilgisi)")
    rag = status.get("rag_stats", {})
    print_status_line("RAG", "Aktif" if rag.get("is_ready") else "Pasif", rag.get("is_ready", False))
    print_metric("Belge Parçası", rag.get("document_chunks", 0))
    print_metric("Sinaptik Bağ", rag.get("synaptic_bonds", 0))

    missing = status.get("missing_modules", [])
    if missing:
        print_sub_header("Eksik Modüller")
        for mod, cmd in missing:
            print(f"    {C.RED}❌ {mod}{C.RESET} → {C.CYAN}{cmd}{C.RESET}")
    print()


def cmd_memory(engine):
    mem = engine.memory.get_stats()
    print_header("HAFIZA (Hebbian Learning)")
    print_status_line("Vektör DB", "Aktif" if mem["db_ready"] else "Pasif", mem["db_ready"])
    print_metric("Toplam Deneyim", mem.get("total_memories", 0))
    print_metric("Hafıza İsabeti", mem.get("hit_count", 0))
    print_metric("Hafıza Kaybı", mem.get("miss_count", 0))
    print_metric_bar("İsabet Oranı", mem.get("hit_rate_percent", 0))
    print()


def cmd_analytics(engine):
    report = engine.analytics.get_full_report()
    print_header("PERFORMANS ANALİTİĞİ")
    print_metric("Toplam Sorgu", report.get("total_queries", 0))
    print_metric("Toplam Hata", report.get("total_errors", 0))
    print_metric("Ort. Yanıt Süresi", f"{report.get('avg_response_time_ms', 0):.0f}ms")
    src_dist = report.get("source_distribution", {})
    if src_dist:
        print_sub_header("Kaynak Dağılımı")
        total = max(1, report.get("total_queries", 1))
        for source, count in src_dist.items():
            print_metric_bar(source, count / total * 100)
    print()


def cmd_routing(engine):
    routing = engine.logic.get_routing_stats()
    print_header("MODEL YÖNLENDİRME (Router)")
    print_metric("Toplam Karar", routing.get("total_decisions", 0))
    print_metric("Basit (Hafif)", routing.get("simple_count", 0))
    print_metric("Karmaşık (Ağır)", routing.get("complex_count", 0))
    print_metric_bar("Karmaşık Oran", routing.get("complex_ratio", 0))
    recent = routing.get("recent_decisions", [])
    if recent:
        print_sub_header("Son Kararlar")
        for dec in reversed(recent):
            level = dec.get("level", "?")
            icon = f"{C.BRIGHT_RED}●{C.RESET}" if level == "complex" else f"{C.BRIGHT_GREEN}●{C.RESET}"
            ts = format_timestamp(dec.get("timestamp", ""))
            print(f"  {icon} [{ts}] {C.BOLD}{level.upper()}{C.RESET} skor:{C.YELLOW}{dec.get('score', 0)}{C.RESET}")
    print()


def cmd_ingest(args: str, ingest_mgr):
    """Dosya yutma komutları."""
    if not args:
        print_info("Kullanım: /ingest <dosya> | /ingest dir | /ingest watch | /ingest status")
        return

    parts = args.strip().split(maxsplit=1)
    subcmd = parts[0].lower()

    if subcmd == "status":
        status = ingest_mgr.get_full_status()
        print_header("DOSYA YUTMA DURUMU")
        vs = status.get("vector_store", {})
        print_metric("Toplam Parça", vs.get("total_chunks", 0))
        files = vs.get("ingested_files", [])
        if files:
            print_sub_header("Yutulmuş Dosyalar")
            for f in files:
                print(f"    {C.CYAN}📄 {f}{C.RESET}")
        watcher = status.get("watcher", {})
        print_status_line("FileWatcher", "Aktif" if watcher.get("is_running") else "Pasif", watcher.get("is_running", False))
        print_metric("İzlenen Klasör", watcher.get("watch_dir", "N/A"))
        stats = status.get("stats", {})
        print_metric("İşlenen Dosya", stats.get("total_files", 0))
        print_metric("Oluşturulan Parça", stats.get("total_chunks", 0))
        print_metric("Hata", stats.get("total_errors", 0))
        print()

    elif subcmd == "dir":
        print_info("./documents klasörü taranıyor...")
        result = ingest_mgr.ingest_directory()
        print_success(f"{result['success_count']} dosya yutuldu, {result['error_count']} hata.")

    elif subcmd == "watch":
        watcher_status = ingest_mgr.watcher.get_status()
        if watcher_status["is_running"]:
            ingest_mgr.stop_watcher()
            print_success("FileWatcher durduruldu.")
        else:
            if ingest_mgr.start_watcher():
                print_success(f"FileWatcher başlatıldı: {ingest_mgr.watcher.watch_dir}")
            else:
                print_error("FileWatcher başlatılamadı.")

    else:
        # Dosya yolu olarak yorumla
        filepath = args.strip()
        if not os.path.exists(filepath):
            print_error(f"Dosya bulunamadı: {filepath}")
            return
        result = ingest_mgr.ingest_file(filepath)
        if result["success"]:
            print_success(
                f"Yutuldu: {result['file_name']} ({result['file_type']}) → "
                f"{result['chunks_stored']} parça"
            )
        else:
            print_error(f"Yutma hatası: {result.get('error', 'Bilinmeyen hata')}")


def cmd_worker(args: str, worker_mgr):
    """Arka plan işçisi komutları."""
    if not args:
        print_info("Kullanım: /worker start | /worker stop | /worker status")
        return

    subcmd = args.strip().lower()

    if subcmd == "start":
        if worker_mgr.start():
            print_success("Hebbian arka plan işçisi başlatıldı.")
        else:
            print_error("Worker başlatılamadı.")

    elif subcmd == "stop":
        worker_mgr.stop()
        print_success("Worker durduruldu.")

    elif subcmd == "status":
        status = worker_mgr.get_full_status()
        print_header("HEBBIAN WORKER DURUMU")
        print_status_line("Worker", "Çalışıyor" if status.get("is_running") else "Durdurulmuş", status.get("is_running", False))
        print_status_line("Yerel Model", "Var" if status.get("has_local_model") else "Yok", status.get("has_local_model", False))
        print_metric("Belge Parçası", status.get("doc_chunk_count", 0))
        print_metric("Sinaptik Bağ", status.get("bond_count", 0))
        stats = status.get("stats", {})
        print_metric("Toplam Döngü", stats.get("total_cycles", 0))
        print_metric("Oluşturulan Bağ", stats.get("total_bonds_stored", 0))
        print_metric("Ort. Döngü Süresi", f"{stats.get('avg_cycle_duration_s', 0):.1f}s")
        proc = status.get("processor", {})
        print_metric_bar("Bağ Oranı", proc.get("bond_rate", 0))
        recent_bonds = stats.get("recent_bonds", [])
        if recent_bonds:
            print_sub_header("Son Sinaptik Bağlar")
            for b in recent_bonds[-3:]:
                print(f"    {C.DIM}[{b.get('bond_type', '?')}]{C.RESET} {C.WHITE}{b.get('preview', '')}{C.RESET}")
        print()

    else:
        print_warning(f"Bilinmeyen worker komutu: {subcmd}")


def cmd_export(chat_history: ChatHistory):
    if chat_history.get_count() == 0:
        print_warning("Henüz sohbet geçmişi yok.")
        return
    print_info(f"Toplam mesaj: {chat_history.get_count()}")
    print(f"  {C.BRIGHT_GREEN}1.{C.RESET} JSON    {C.BRIGHT_GREEN}2.{C.RESET} Metin    {C.BRIGHT_GREEN}3.{C.RESET} İptal")
    try:
        choice = input(f"  {C.DIM}Seçim:{C.RESET} ").strip()
    except (EOFError, KeyboardInterrupt):
        return
    if choice == "1":
        path = chat_history.export_json()
        print_success(f"Kaydedildi: {path}")
    elif choice == "2":
        path = chat_history.export_text()
        print_success(f"Kaydedildi: {path}")
    else:
        print_info("İptal.")


def cmd_clear():
    clear_screen()
    print(QUARK_BANNER)


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 6 — BAŞLANGIÇ
# ════════════════════════════════════════════════════════════════

def print_startup_status(engine):
    if engine.local_model.is_loaded:
        print_success(f"Yerel model aktif: {engine.local_model.model_name}")
    else:
        if engine.local_model.load_error:
            for line in engine.local_model.load_error.split("\n"):
                print_warning(line.strip())

    mem_stats = engine.memory.get_stats()
    if mem_stats.get("db_ready"):
        print_success(f"Vektör bellek aktif: {mem_stats.get('total_memories', 0)} deneyim")

    rag_stats = engine.rag.get_stats()
    if rag_stats.get("is_ready"):
        doc_count = rag_stats.get("document_chunks", 0)
        bond_count = rag_stats.get("synaptic_bonds", 0)
        if doc_count > 0 or bond_count > 0:
            print_success(f"RAG aktif: {doc_count} belge parçası, {bond_count} sinaptik bağ")

    if engine.has_any_engine():
        print_info(f"{C.BRIGHT_GREEN}Q1 sohbete hazır.{C.RESET}")
    else:
        print_error("Yerel model bulunamadı!")
        print_info(".gguf dosyasını proje dizinine koyun.")


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 7 — YANIT İŞLEME
# ════════════════════════════════════════════════════════════════

def process_response(result, output_layer, show_thinking, chat_history, elapsed_ms):
    formatted = output_layer.format_for_display(result)
    display_content = formatted["display_content"]
    thinking_chain = formatted.get("thinking_chain", "")
    source = result.get("source", "UNKNOWN")
    model = result.get("model", "unknown")
    confidence = result.get("confidence", 0.0)
    revised = result.get("revised", False)
    engine_type = result.get("engine", "")

    if show_thinking and thinking_chain:
        print_thinking(thinking_chain)

    print_q1_response(display_content)
    print_meta(source, model, confidence, elapsed_ms, revised, engine_type)

    chat_history.add_q1(display_content, source, model, confidence, elapsed_ms, revised)


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 8 — ANA DÖNGÜ
# ════════════════════════════════════════════════════════════════

def main():
    if os.name == 'nt':
        os.system('')

    clear_screen()
    print(QUARK_BANNER)
    print(f"  {C.DIM}Q1 Engine yükleniyor...{C.RESET}\n")

    # ── Q1 Engine ──
    try:
        from brain import Q1Engine, OutputLayer
        engine = Q1Engine()
        output_layer = OutputLayer()
        print_success("Q1 Engine başlatıldı.")
    except ImportError as e:
        print_error(f"Modül eksik: {e}")
        print_info("pip install -r requirements.txt")
        return
    except Exception as e:
        print_error(f"Q1 Engine hatası: {e}")
        return

    # ── Ingestor + Otomatik Ezber ──
    ingest_mgr = None
    try:
        from ingestor import IngestManager
        ingest_mgr = IngestManager()
        print_success("Ingestor hazır.")

        # brain_data klasörünü oluştur (yoksa)
        brain_data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "brain_data")
        os.makedirs(brain_data_dir, exist_ok=True)

        # Mevcut dosyaları otomatik yut (boot-time ingest)
        boot_result = ingest_mgr.ingest_directory(brain_data_dir)
        if boot_result["total_files"] > 0:
            print_success(
                f"brain_data tarandı: {boot_result['success_count']} dosya yutuldu "
                f"({boot_result['error_count']} hata)"
            )

        # FileWatcher'ı otomatik başlat — brain_data sürekli dinlenecek
        if ingest_mgr.start_watcher():
            print_success(f"FileWatcher aktif: {brain_data_dir}")
        else:
            print_warning("FileWatcher başlatılamadı (watchdog eksik olabilir).")

    except Exception as e:
        print_warning(f"Ingestor yüklenemedi: {e}")

    # ── Worker + Otomatik Hebbian Öğrenme ──
    worker_mgr = None
    try:
        from worker import WorkerManager
        worker_mgr = WorkerManager(engine.local_model)
        print_success("Worker hazır.")

        # Arka plan Hebbian öğrenme döngüsünü otomatik başlat
        if worker_mgr.start():
            print_success("Hebbian öğrenme döngüsü arka planda çalışıyor.")
        else:
            print_warning("Worker başlatılamadı (parça eksik veya chromadb yok).")

    except Exception as e:
        print_warning(f"Worker yüklenemedi: {e}")

    # ── Durum ──
    print_startup_status(engine)

    print()
    print_divider()
    print(f"  {C.DIM}Yardım: {C.BRIGHT_GREEN}/help{C.DIM}  Çıkış: {C.BRIGHT_GREEN}/quit{C.RESET}")
    print_divider()

    show_thinking = False
    chat_history = ChatHistory()

    # ── Döngü ──
    while True:
        try:
            print()
            user_input = input(f"  {C.BRIGHT_GREEN}{C.BOLD}⚛ Quark ▸{C.RESET} ").strip()

            if not user_input:
                continue

            if user_input.startswith("/"):
                parts = user_input.split(maxsplit=1)
                cmd = parts[0].lower()
                args = parts[1] if len(parts) > 1 else ""

                if cmd in ("/quit", "/exit", "/q"):
                    if worker_mgr and worker_mgr.worker.is_running:
                        worker_mgr.stop()
                    if ingest_mgr and ingest_mgr.watcher.is_running:
                        ingest_mgr.stop_watcher()
                    print(GOODBYE_TEXT)
                    break
                elif cmd in ("/help", "/h"):
                    cmd_help()
                elif cmd in ("/status", "/s"):
                    cmd_status(engine)
                elif cmd in ("/memory", "/m"):
                    cmd_memory(engine)
                elif cmd in ("/analytics", "/a"):
                    cmd_analytics(engine)
                elif cmd in ("/routing", "/r"):
                    cmd_routing(engine)
                elif cmd in ("/think", "/t"):
                    show_thinking = not show_thinking
                    state = "AKTİF" if show_thinking else "PASİF"
                    color = C.BRIGHT_GREEN if show_thinking else C.BRIGHT_RED
                    print(f"\n  {C.BRIGHT_YELLOW}💭{C.RESET} Düşünce Zinciri: {color}{C.BOLD}{state}{C.RESET}")
                elif cmd == "/ingest":
                    if ingest_mgr:
                        cmd_ingest(args, ingest_mgr)
                    else:
                        print_error("Ingestor modülü yüklenemedi.")
                elif cmd == "/worker":
                    if worker_mgr:
                        cmd_worker(args, worker_mgr)
                    else:
                        print_error("Worker modülü yüklenemedi.")
                elif cmd in ("/export", "/e"):
                    cmd_export(chat_history)
                elif cmd in ("/clear", "/c"):
                    cmd_clear()
                else:
                    print_warning(f"Bilinmeyen komut: {cmd}. /help yazın.")
                continue

            # ── Q1 ile Konuşma ──
            print_user_message(user_input)
            chat_history.add_user(user_input)

            sys.stdout.write(f"\n  {C.DIM}⚛ Q1 düşünüyor...{C.RESET}")
            sys.stdout.flush()

            start_time = time.time()
            result = engine.think(user_input)
            elapsed_ms = (time.time() - start_time) * 1000

            sys.stdout.write(f"\r  {' ' * 50}\r")
            sys.stdout.flush()

            process_response(result, output_layer, show_thinking, chat_history, elapsed_ms)

        except KeyboardInterrupt:
            if worker_mgr and worker_mgr.worker.is_running:
                worker_mgr.stop()
            print(GOODBYE_TEXT)
            break
        except EOFError:
            print(GOODBYE_TEXT)
            break
        except Exception as e:
            print_error(f"Beklenmeyen hata: {e}")


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 9 — GİRİŞ NOKTASI
# ════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    main()

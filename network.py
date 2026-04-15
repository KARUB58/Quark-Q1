"""
╔══════════════════════════════════════════════════════════════════╗
║               QUARK — MERGENCE NETWORK MODULE                    ║
║         P2P Ağ İletişimi • Deneyim Paylaşımı • Keşif            ║
║             Peer Discovery • Health Monitoring                   ║
╚══════════════════════════════════════════════════════════════════╝

Mergence Network, birden fazla Quark düğümünün birbirleriyle
iletişim kurarak kolektif zekayı güçlendirdiği P2P ağ katmanıdır.

Bölümler:
    1. NetworkConfig      — Ağ yapılandırması ve sabitleri
    2. MessageProtocol    — Mesaj protokolü ve serileştirme
    3. PeerRegistry       — Düğüm kayıt defteri ve yönetimi
    4. HealthMonitor      — Düğüm sağlık izleme
    5. ConnectionPool     — Bağlantı havuzu
    6. MergenceNetwork    — Ana ağ sınıfı (yayın, dinleme, keşif)
    7. NetworkAnalytics   — Ağ istatistikleri

Yazar  : Quark Technologies
Sürüm  : 2.0.0
"""

import socket
import json
import threading
import time
import hashlib
import uuid
from datetime import datetime, timezone
from collections import defaultdict


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 1 — AĞ YAPILANDIRMASI VE SABİTLER
# ════════════════════════════════════════════════════════════════

class NetworkConfig:
    """
    Mergence Network için tüm yapılandırma sabitleri.
    Tek bir yerden yönetim sağlar.
    """

    # Ağ port numaraları
    DEFAULT_PORT         = 5005
    DISCOVERY_PORT       = 5006
    HEALTH_CHECK_PORT    = 5007

    # Zaman aşımı süreleri (saniye)
    CONNECTION_TIMEOUT   = 2.0
    HEALTH_CHECK_TIMEOUT = 1.0
    DISCOVERY_INTERVAL   = 30.0     # Düğüm keşfi aralığı
    HEALTH_CHECK_INTERVAL = 15.0    # Sağlık kontrolü aralığı

    # Mesaj boyutu limitleri
    MAX_MESSAGE_SIZE     = 65536    # 64 KB
    BUFFER_SIZE          = 8192     # 8 KB okuma tamponu

    # Bağlantı havuzu
    MAX_CONNECTIONS      = 50
    MAX_PEERS            = 100

    # Protokol sabitleri
    PROTOCOL_VERSION     = "2.0"
    NODE_TYPE            = "QUARK_Q1"

    # Yeniden deneme ayarları
    MAX_RETRIES          = 3
    RETRY_DELAY          = 0.5      # saniye

    # Broadcast subnet tarama aralığı
    SUBNET_SCAN_RANGE    = 20       # 192.168.1.1 - 192.168.1.20 gibi


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 2 — MESAJ PROTOKOLÜ
# ════════════════════════════════════════════════════════════════

class MessageProtocol:
    """
    Mergence ağı üzerindeki tüm mesajların yapısını tanımlar.
    JSON tabanlı serileştirme ile iletişim.
    """

    # Mesaj tipleri
    TYPE_REQUEST        = "REQ"       # Bilgi talebi
    TYPE_RESPONSE       = "RES"       # Bilgi yanıtı
    TYPE_PING           = "PING"      # Sağlık kontrolü
    TYPE_PONG           = "PONG"      # Sağlık yanıtı
    TYPE_DISCOVER       = "DISCOVER"  # Düğüm keşfi
    TYPE_ANNOUNCE       = "ANNOUNCE"  # Düğüm duyurusu
    TYPE_SYNC           = "SYNC"      # Deneyim senkronizasyonu
    TYPE_SYNC_ACK       = "SYNC_ACK"  # Senkronizasyon onayı

    # Yanıt durumları
    STATUS_FOUND         = "FOUND"
    STATUS_NOT_FOUND     = "NOT_FOUND"
    STATUS_ERROR         = "ERROR"
    STATUS_OK            = "OK"

    @staticmethod
    def create_message(msg_type: str, payload: dict = None) -> str:
        """
        Standart bir ağ mesajı oluşturur.

        Yapı:
            {
                "type": "REQ",
                "id": "uuid",
                "version": "2.0",
                "timestamp": "iso-date",
                "node_type": "QUARK_Q1",
                "payload": { ... }
            }
        """
        message = {
            "type": msg_type,
            "id": str(uuid.uuid4()),
            "version": NetworkConfig.PROTOCOL_VERSION,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "node_type": NetworkConfig.NODE_TYPE,
            "payload": payload or {},
        }
        return json.dumps(message, ensure_ascii=False)

    @staticmethod
    def create_request(query: str) -> str:
        """Bilgi talep mesajı oluşturur."""
        return MessageProtocol.create_message(
            MessageProtocol.TYPE_REQUEST,
            {"query": query}
        )

    @staticmethod
    def create_response(status: str, result: str = None, confidence: float = 0.0) -> str:
        """Bilgi yanıt mesajı oluşturur."""
        return MessageProtocol.create_message(
            MessageProtocol.TYPE_RESPONSE,
            {
                "status": status,
                "result": result,
                "confidence": confidence,
            }
        )

    @staticmethod
    def create_ping(node_id: str = None) -> str:
        """Sağlık kontrolü mesajı oluşturur."""
        return MessageProtocol.create_message(
            MessageProtocol.TYPE_PING,
            {"node_id": node_id or str(uuid.uuid4())}
        )

    @staticmethod
    def create_pong(node_id: str, uptime_seconds: float = 0.0) -> str:
        """Sağlık yanıtı mesajı oluşturur."""
        return MessageProtocol.create_message(
            MessageProtocol.TYPE_PONG,
            {
                "node_id": node_id,
                "uptime_seconds": uptime_seconds,
                "status": "ALIVE",
            }
        )

    @staticmethod
    def create_discover() -> str:
        """Düğüm keşif mesajı oluşturur."""
        return MessageProtocol.create_message(
            MessageProtocol.TYPE_DISCOVER,
            {"seeking": "QUARK_NODES"}
        )

    @staticmethod
    def create_announce(node_info: dict) -> str:
        """Düğüm duyuru mesajı oluşturur."""
        return MessageProtocol.create_message(
            MessageProtocol.TYPE_ANNOUNCE,
            node_info
        )

    @staticmethod
    def create_sync(experience_data: dict) -> str:
        """Deneyim senkronizasyon mesajı oluşturur."""
        return MessageProtocol.create_message(
            MessageProtocol.TYPE_SYNC,
            experience_data
        )

    @staticmethod
    def parse_message(raw_data: bytes) -> dict:
        """
        Ham veriyi parse ederek mesaj sözlüğüne dönüştürür.
        Hatalı mesajları güvenli şekilde yakalar.
        """
        try:
            decoded = raw_data.decode("utf-8")
            message = json.loads(decoded)

            # Zorunlu alanları doğrula
            required_fields = ["type", "id"]
            for field in required_fields:
                if field not in message:
                    return {
                        "type": "INVALID",
                        "error": f"Eksik alan: {field}",
                        "raw": decoded[:200],
                    }

            return message

        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            return {
                "type": "INVALID",
                "error": str(e),
                "raw": str(raw_data[:200]),
            }


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 3 — DÜĞÜM KAYIT DEFTERİ (Peer Registry)
# ════════════════════════════════════════════════════════════════

class PeerInfo:
    """Tek bir peer düğümünün bilgilerini tutar."""

    def __init__(self, ip: str, port: int = NetworkConfig.DEFAULT_PORT):
        self.ip = ip
        self.port = port
        self.node_id = hashlib.md5(f"{ip}:{port}".encode()).hexdigest()[:12]
        self.first_seen = datetime.now(timezone.utc)
        self.last_seen = datetime.now(timezone.utc)
        self.is_alive = True
        self.failed_pings = 0
        self.successful_queries = 0
        self.failed_queries = 0
        self.total_response_time_ms = 0.0
        self.node_type = "UNKNOWN"

    def mark_alive(self):
        """Düğümü canlı olarak işaretle."""
        self.last_seen = datetime.now(timezone.utc)
        self.is_alive = True
        self.failed_pings = 0

    def mark_failed(self):
        """Başarısız ping kaydı."""
        self.failed_pings += 1
        if self.failed_pings >= 3:
            self.is_alive = False

    def record_query(self, success: bool, response_time_ms: float = 0.0):
        """Sorgu sonucunu kaydeder."""
        if success:
            self.successful_queries += 1
        else:
            self.failed_queries += 1
        self.total_response_time_ms += response_time_ms

    def get_avg_response_time(self) -> float:
        """Ortalama yanıt süresini hesaplar."""
        total = self.successful_queries + self.failed_queries
        if total == 0:
            return 0.0
        return self.total_response_time_ms / total

    def to_dict(self) -> dict:
        """Sözlük formatına dönüştürür."""
        return {
            "node_id": self.node_id,
            "ip": self.ip,
            "port": self.port,
            "is_alive": self.is_alive,
            "first_seen": self.first_seen.isoformat(),
            "last_seen": self.last_seen.isoformat(),
            "failed_pings": self.failed_pings,
            "successful_queries": self.successful_queries,
            "failed_queries": self.failed_queries,
            "avg_response_time_ms": round(self.get_avg_response_time(), 2),
            "node_type": self.node_type,
        }


class PeerRegistry:
    """
    Ağdaki tüm bilinen düğümlerin kayıt defteri.
    Thread-safe erişim sağlar.
    """

    def __init__(self, max_peers: int = NetworkConfig.MAX_PEERS):
        self.peers = {}         # ip -> PeerInfo
        self.max_peers = max_peers
        self._lock = threading.Lock()

    def add_peer(self, ip: str, port: int = NetworkConfig.DEFAULT_PORT) -> PeerInfo:
        """Yeni bir peer ekler veya mevcut olanı günceller."""
        with self._lock:
            if ip in self.peers:
                self.peers[ip].mark_alive()
                return self.peers[ip]

            if len(self.peers) >= self.max_peers:
                # En eski inaktif peer'ı kaldır
                self._evict_oldest_inactive()

            peer = PeerInfo(ip, port)
            self.peers[ip] = peer
            return peer

    def remove_peer(self, ip: str) -> bool:
        """Bir peer'ı kaldırır."""
        with self._lock:
            if ip in self.peers:
                del self.peers[ip]
                return True
            return False

    def get_peer(self, ip: str) -> PeerInfo:
        """Belirli bir peer'ın bilgisini döner."""
        with self._lock:
            return self.peers.get(ip)

    def get_alive_peers(self) -> list:
        """Canlı peer listesini döner."""
        with self._lock:
            return [p for p in self.peers.values() if p.is_alive]

    def get_all_peers(self) -> list:
        """Tüm peer listesini döner."""
        with self._lock:
            return list(self.peers.values())

    def get_peer_ips(self) -> set:
        """Canlı peer IP adreslerini döner."""
        with self._lock:
            return {p.ip for p in self.peers.values() if p.is_alive}

    def _evict_oldest_inactive(self):
        """En eski inaktif peer'ı kaldırır."""
        inactive = [p for p in self.peers.values() if not p.is_alive]
        if inactive:
            oldest = min(inactive, key=lambda p: p.last_seen)
            del self.peers[oldest.ip]

    def get_stats(self) -> dict:
        """Kayıt defteri istatistiklerini döner."""
        with self._lock:
            total = len(self.peers)
            alive = sum(1 for p in self.peers.values() if p.is_alive)
            return {
                "total_peers": total,
                "alive_peers": alive,
                "dead_peers": total - alive,
                "max_peers": self.max_peers,
            }


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 4 — SAĞLIK İZLEME (Health Monitor)
# ════════════════════════════════════════════════════════════════

class HealthMonitor:
    """
    Ağdaki düğümlerin sağlık durumunu periyodik olarak kontrol eder.
    Ping/Pong mekanizması ile çalışır.
    """

    def __init__(self, registry: PeerRegistry, port: int = NetworkConfig.DEFAULT_PORT):
        self.registry = registry
        self.port = port
        self.is_running = False
        self._thread = None
        self.check_count = 0
        self.last_check_time = None

    def ping_peer(self, ip: str, timeout: float = NetworkConfig.HEALTH_CHECK_TIMEOUT) -> bool:
        """
        Tek bir peer'a ping gönderir.
        Yanıt alırsa True, alamazsa False döner.
        """
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(timeout)
                s.connect((ip, self.port))

                ping_msg = MessageProtocol.create_ping()
                s.sendall(ping_msg.encode("utf-8"))

                data = s.recv(NetworkConfig.BUFFER_SIZE)
                if data:
                    response = MessageProtocol.parse_message(data)
                    if response.get("type") == MessageProtocol.TYPE_PONG:
                        return True

            return False

        except (socket.timeout, ConnectionRefusedError, OSError):
            return False

    def check_all_peers(self):
        """Tüm kayıtlı peer'ların sağlığını kontrol eder."""
        peers = self.registry.get_all_peers()
        self.check_count += 1
        self.last_check_time = datetime.now(timezone.utc).isoformat()

        for peer in peers:
            is_alive = self.ping_peer(peer.ip)
            if is_alive:
                peer.mark_alive()
            else:
                peer.mark_failed()

    def start(self, interval: float = NetworkConfig.HEALTH_CHECK_INTERVAL):
        """
        Sağlık kontrolü döngüsünü arka planda başlatır.
        """
        if self.is_running:
            return

        self.is_running = True

        def monitor_loop():
            while self.is_running:
                try:
                    self.check_all_peers()
                except Exception:
                    pass
                time.sleep(interval)

        self._thread = threading.Thread(target=monitor_loop, daemon=True)
        self._thread.start()

    def stop(self):
        """Sağlık kontrolü döngüsünü durdurur."""
        self.is_running = False

    def get_stats(self) -> dict:
        """İzleme istatistiklerini döner."""
        return {
            "is_running": self.is_running,
            "check_count": self.check_count,
            "last_check_time": self.last_check_time,
        }


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 5 — BAĞLANTI HAVUZU (Connection Pool)
# ════════════════════════════════════════════════════════════════

class ConnectionPool:
    """
    TCP bağlantılarını yönetir.
    Gereksiz bağlantı açma/kapama overhead'ini azaltır.
    """

    def __init__(self, max_connections: int = NetworkConfig.MAX_CONNECTIONS):
        self.max_connections = max_connections
        self.active_connections = 0
        self._lock = threading.Lock()
        self.total_created = 0
        self.total_failed = 0
        self.connection_log = []

    def create_connection(self, ip: str, port: int,
                          timeout: float = NetworkConfig.CONNECTION_TIMEOUT) -> socket.socket:
        """
        Yeni bir TCP bağlantı oluşturur.
        Havuz limiti aşıldığında None döner.
        """
        with self._lock:
            if self.active_connections >= self.max_connections:
                self.total_failed += 1
                return None

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((ip, port))

            with self._lock:
                self.active_connections += 1
                self.total_created += 1

            self.connection_log.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ip": ip,
                "port": port,
                "action": "CREATED",
            })

            return s

        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            with self._lock:
                self.total_failed += 1

            self.connection_log.append({
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "ip": ip,
                "port": port,
                "action": "FAILED",
                "error": str(e),
            })
            return None

    def release_connection(self, s: socket.socket):
        """Bağlantıyı serbest bırakır ve kapatır."""
        try:
            s.close()
        except Exception:
            pass
        finally:
            with self._lock:
                self.active_connections = max(0, self.active_connections - 1)

    def get_stats(self) -> dict:
        """Havuz istatistiklerini döner."""
        return {
            "active_connections": self.active_connections,
            "max_connections": self.max_connections,
            "total_created": self.total_created,
            "total_failed": self.total_failed,
            "recent_log": self.connection_log[-10:] if self.connection_log else [],
        }


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 6 — AĞ ANALİTİĞİ (Network Analytics)
# ════════════════════════════════════════════════════════════════

class NetworkAnalytics:
    """
    Mergence ağı performans izleme ve raporlama.
    """

    def __init__(self):
        self.start_time = datetime.now(timezone.utc)
        self.total_broadcasts = 0
        self.total_received = 0
        self.total_syncs = 0
        self.total_discoveries = 0
        self.successful_queries = 0
        self.failed_queries = 0
        self.bytes_sent = 0
        self.bytes_received = 0
        self.event_log = []

    def record_broadcast(self, query: str, success: bool):
        """Yayın olayını kaydeder."""
        self.total_broadcasts += 1
        if success:
            self.successful_queries += 1
        else:
            self.failed_queries += 1

        self.event_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "BROADCAST",
            "query": query[:100],
            "success": success,
        })
        if len(self.event_log) > 100:
            self.event_log = self.event_log[-100:]

    def record_received(self, msg_type: str, from_ip: str):
        """Alınan mesajı kaydeder."""
        self.total_received += 1
        self.event_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "RECEIVED",
            "msg_type": msg_type,
            "from_ip": from_ip,
        })

    def record_sync(self, peer_ip: str, success: bool):
        """Senkronizasyon olayını kaydeder."""
        self.total_syncs += 1
        self.event_log.append({
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "type": "SYNC",
            "peer_ip": peer_ip,
            "success": success,
        })

    def record_bytes(self, sent: int = 0, received: int = 0):
        """Gönderilen/alınan byte miktarını kaydeder."""
        self.bytes_sent += sent
        self.bytes_received += received

    def get_uptime_seconds(self) -> float:
        """Çalışma süresini saniye cinsinden döner."""
        delta = datetime.now(timezone.utc) - self.start_time
        return delta.total_seconds()

    def get_full_report(self) -> dict:
        """Kapsamlı ağ raporu."""
        uptime = self.get_uptime_seconds()
        total_queries = self.successful_queries + self.failed_queries
        success_rate = (
            self.successful_queries / total_queries * 100
            if total_queries > 0 else 0.0
        )

        return {
            "uptime_seconds": round(uptime, 2),
            "total_broadcasts": self.total_broadcasts,
            "total_received": self.total_received,
            "total_syncs": self.total_syncs,
            "total_discoveries": self.total_discoveries,
            "successful_queries": self.successful_queries,
            "failed_queries": self.failed_queries,
            "success_rate_percent": round(success_rate, 2),
            "bytes_sent": self.bytes_sent,
            "bytes_received": self.bytes_received,
            "recent_events": self.event_log[-20:],
        }


# ════════════════════════════════════════════════════════════════
#  BÖLÜM 7 — MERGENCE NETWORK (Ana Ağ Sınıfı)
# ════════════════════════════════════════════════════════════════

class MergenceNetwork:
    """
    Quark düğümleri arasında P2P iletişim sağlayan ana ağ sınıfı.

    Yetenekler:
        - broadcast_query  : Ağdaki herkese soru sorar
        - start_listener   : Diğer düğümlerin sorularını dinler
        - start_discovery  : Yeni düğümleri otomatik keşfeder
        - sync_experience  : Deneyim paylaşımı yapar
    """

    def __init__(self, brain_ref, port: int = NetworkConfig.DEFAULT_PORT):
        """
        Mergence Network'ü başlatır.

        Parametreler:
            brain_ref : Q1Engine referansı (think ve memory erişimi için)
            port      : Dinleme portu
        """
        self.brain = brain_ref
        self.port = port
        self.node_id = str(uuid.uuid4())[:8]

        # Alt sistemler
        self.registry = PeerRegistry()
        self.health_monitor = HealthMonitor(self.registry, port)
        self.connection_pool = ConnectionPool()
        self.analytics = NetworkAnalytics()

        # Durumlar
        self.is_listening = False
        self.is_discovering = False

    def add_peer(self, ip: str, port: int = None) -> PeerInfo:
        """Manuel olarak peer ekler."""
        return self.registry.add_peer(ip, port or self.port)

    def remove_peer(self, ip: str) -> bool:
        """Peer'ı kaldırır."""
        return self.registry.remove_peer(ip)

    def broadcast_query(self, question: str) -> dict:
        """
        Ağdaki tüm canlı düğümlere soruyu yayınlar.

        Dönüş:
            {
                "success": bool,
                "result": str or None,
                "from_peer": str or None,
                "peers_queried": int,
                "elapsed_ms": float,
            }
        """
        print(f"🌐 [MERGENCE] '{question[:80]}' için kovan zekasına soruluyor...")

        alive_peers = self.registry.get_alive_peers()
        start_time = time.time()
        peers_queried = 0

        for peer in alive_peers:
            peers_queried += 1
            try:
                conn = self.connection_pool.create_connection(peer.ip, peer.port)
                if not conn:
                    peer.record_query(False)
                    continue

                try:
                    request = MessageProtocol.create_request(question)
                    request_bytes = request.encode("utf-8")
                    conn.sendall(request_bytes)
                    self.analytics.record_bytes(sent=len(request_bytes))

                    data = conn.recv(NetworkConfig.MAX_MESSAGE_SIZE)
                    if data:
                        self.analytics.record_bytes(received=len(data))
                        response = MessageProtocol.parse_message(data)

                        payload = response.get("payload", {})
                        status = payload.get("status", "")

                        if status == MessageProtocol.STATUS_FOUND:
                            result = payload.get("result", "")
                            elapsed_ms = (time.time() - start_time) * 1000

                            print(f"✅ {peer.ip} biriminden bilgi ışınlandı!")

                            # Deneyimi hafızaya kaydet (Hebbian Learning)
                            if hasattr(self.brain, "memory") and hasattr(self.brain.memory, "store_experience"):
                                self.brain.memory.store_experience(question, result)
                            elif hasattr(self.brain, "learn_hebbian"):
                                self.brain.learn_hebbian(question, result)

                            peer.record_query(True, elapsed_ms)
                            peer.mark_alive()
                            self.analytics.record_broadcast(question, True)

                            return {
                                "success": True,
                                "result": result,
                                "from_peer": peer.ip,
                                "peers_queried": peers_queried,
                                "elapsed_ms": round(elapsed_ms, 2),
                                "confidence": payload.get("confidence", 0.9),
                            }

                    peer.record_query(False)

                finally:
                    self.connection_pool.release_connection(conn)

            except Exception:
                peer.record_query(False)
                continue

        elapsed_ms = (time.time() - start_time) * 1000
        self.analytics.record_broadcast(question, False)

        return {
            "success": False,
            "result": None,
            "from_peer": None,
            "peers_queried": peers_queried,
            "elapsed_ms": round(elapsed_ms, 2),
            "confidence": 0.0,
        }

    def _handle_client(self, conn: socket.socket, addr: tuple):
        """
        Gelen bir bağlantıyı işler.
        Mesaj tipine göre uygun yanıt üretir.
        """
        try:
            data = conn.recv(NetworkConfig.MAX_MESSAGE_SIZE)
            if not data:
                return

            self.analytics.record_bytes(received=len(data))
            message = MessageProtocol.parse_message(data)
            msg_type = message.get("type", "")
            payload = message.get("payload", {})

            self.analytics.record_received(msg_type, addr[0])

            # Peer'ı kaydet
            self.registry.add_peer(addr[0])

            # ── REQ: Bilgi Talebi ──
            if msg_type == MessageProtocol.TYPE_REQUEST:
                query = payload.get("query", "")
                if query and self.brain:
                    thought_obj = self.brain.think(query)
                    if thought_obj and thought_obj.get("content"):
                        response = MessageProtocol.create_response(
                            MessageProtocol.STATUS_FOUND,
                            thought_obj["content"],
                            thought_obj.get("confidence", 0.9)
                        )
                    else:
                        response = MessageProtocol.create_response(
                            MessageProtocol.STATUS_NOT_FOUND
                        )
                else:
                    response = MessageProtocol.create_response(
                        MessageProtocol.STATUS_NOT_FOUND
                    )

                response_bytes = response.encode("utf-8")
                conn.sendall(response_bytes)
                self.analytics.record_bytes(sent=len(response_bytes))

            # ── PING: Sağlık Kontrolü ──
            elif msg_type == MessageProtocol.TYPE_PING:
                pong = MessageProtocol.create_pong(
                    self.node_id,
                    self.analytics.get_uptime_seconds()
                )
                pong_bytes = pong.encode("utf-8")
                conn.sendall(pong_bytes)
                self.analytics.record_bytes(sent=len(pong_bytes))

            # ── DISCOVER: Düğüm Keşfi ──
            elif msg_type == MessageProtocol.TYPE_DISCOVER:
                self.analytics.total_discoveries += 1
                announcement = MessageProtocol.create_announce({
                    "node_id": self.node_id,
                    "port": self.port,
                    "node_type": NetworkConfig.NODE_TYPE,
                    "uptime": self.analytics.get_uptime_seconds(),
                })
                announce_bytes = announcement.encode("utf-8")
                conn.sendall(announce_bytes)
                self.analytics.record_bytes(sent=len(announce_bytes))

            # ── SYNC: Deneyim Senkronizasyonu ──
            elif msg_type == MessageProtocol.TYPE_SYNC:
                experience = payload.get("experience", {})
                prompt = experience.get("prompt", "")
                response_text = experience.get("response", "")

                if prompt and response_text and hasattr(self.brain, "memory"):
                    self.brain.memory.store_experience(prompt, response_text)
                    self.analytics.record_sync(addr[0], True)

                    ack = MessageProtocol.create_message(
                        MessageProtocol.TYPE_SYNC_ACK,
                        {"status": "OK"}
                    )
                    conn.sendall(ack.encode("utf-8"))
                else:
                    self.analytics.record_sync(addr[0], False)

        except Exception:
            pass
        finally:
            try:
                conn.close()
            except Exception:
                pass

    def start_listener(self):
        """
        Ağdan gelen istekleri dinleyen sunucuyu arka planda başlatır.
        """
        if self.is_listening:
            return

        self.is_listening = True

        def listen_loop():
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
                    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    server.bind(('0.0.0.0', self.port))
                    server.listen(NetworkConfig.MAX_CONNECTIONS)
                    server.settimeout(1.0)

                    print(f"📡 [MERGENCE] Dinleyici başlatıldı — Port: {self.port}")

                    while self.is_listening:
                        try:
                            conn, addr = server.accept()
                            handler_thread = threading.Thread(
                                target=self._handle_client,
                                args=(conn, addr),
                                daemon=True
                            )
                            handler_thread.start()
                        except socket.timeout:
                            continue
                        except Exception:
                            continue

            except Exception as e:
                print(f"❌ [MERGENCE] Dinleyici hatası: {e}")
                self.is_listening = False

        self._listener_thread = threading.Thread(target=listen_loop, daemon=True)
        self._listener_thread.start()

    def stop_listener(self):
        """Dinleyiciyi durdurur."""
        self.is_listening = False

    def sync_experience_to_peer(self, peer_ip: str, prompt: str, response: str) -> bool:
        """
        Belirli bir peer'a deneyim gönderir.
        """
        try:
            conn = self.connection_pool.create_connection(peer_ip, self.port)
            if not conn:
                return False

            try:
                sync_msg = MessageProtocol.create_sync({
                    "experience": {
                        "prompt": prompt,
                        "response": response,
                        "from_node": self.node_id,
                    }
                })
                conn.sendall(sync_msg.encode("utf-8"))
                self.analytics.record_bytes(sent=len(sync_msg))

                data = conn.recv(NetworkConfig.BUFFER_SIZE)
                if data:
                    ack = MessageProtocol.parse_message(data)
                    if ack.get("type") == MessageProtocol.TYPE_SYNC_ACK:
                        self.analytics.record_sync(peer_ip, True)
                        return True

                self.analytics.record_sync(peer_ip, False)
                return False

            finally:
                self.connection_pool.release_connection(conn)

        except Exception:
            self.analytics.record_sync(peer_ip, False)
            return False

    def sync_experience_to_all(self, prompt: str, response: str) -> dict:
        """Tüm canlı peer'lara deneyim gönderir."""
        alive_peers = self.registry.get_alive_peers()
        results = {"success": 0, "failed": 0}

        for peer in alive_peers:
            if self.sync_experience_to_peer(peer.ip, prompt, response):
                results["success"] += 1
            else:
                results["failed"] += 1

        return results

    def start_health_monitoring(self):
        """Sağlık izlemeyi başlatır."""
        self.health_monitor.start()

    def stop_health_monitoring(self):
        """Sağlık izlemeyi durdurur."""
        self.health_monitor.stop()

    def get_network_status(self) -> dict:
        """Kapsamlı ağ durumu raporu."""
        return {
            "node_id": self.node_id,
            "port": self.port,
            "is_listening": self.is_listening,
            "is_discovering": self.is_discovering,
            "registry": self.registry.get_stats(),
            "health": self.health_monitor.get_stats(),
            "connections": self.connection_pool.get_stats(),
            "analytics": self.analytics.get_full_report(),
        }

# Serving-Blueprint Analizi ve Geliştirme Planı

## 📊 İş Akışı (Workflow) Diyagramı

```
┌──────────┐     ┌──────────┐     ┌──────────────┐     ┌──────────┐     ┌──────────┐
│          │     │          │     │              │     │          │     │          │
│  Client  │────▶│  FastAPI │────▶│ Celery Task  │────▶│  Worker  │────▶│  Redis   │
│          │     │          │     │              │     │          │     │          │
└──────────┘     └──────────┘     └──────────────┘     └──────────┘     └──────────┘
      │                ▲                                     │                 │
      │                │                                     │                 │
      │                │                                     ▼                 │
      │                │               ┌──────────────────────────────┐       │
      │                │               │                              │       │
      │                │               │  TextEmbeddingService        │       │
      │                │               │  (light_embed kütüphanesi)   │       │
      │                │               │                              │       │
      │                │               └──────────────────────────────┘       │
      │                │                                                      │
      │                │                                                      │
      └────────────────┴──────────────────────────────────────────────────────┘
         Task ID ile                           Sonuç sorgusu
         sonuç sorgusu
```

## 💻 Temel Sınıflar ve Bileşenler

| Sınıf/Bileşen | Açıklama | Kullanım Amacı |
|---------------|----------|----------------|
| **FastAPI** | Web framework | API uç noktaları oluşturmak ve HTTP isteklerini yönetmek için kullanılır |
| **TextEmbeddingService** | ML model hizmeti | Metin gömme (text embedding) işlemini gerçekleştiren, modelleri yükleyip tahminler yapan ana sınıf |
| **TextEmbeddingWorkerService** | Celery entegrasyon sınıfı | Asenkron görevleri Celery'ye göndermek ve sonuçları almak için kullanılır |
| **Celery** | Asenkron görev kuyruğu | CPU yoğun işlemleri arka planda çalıştırmak için kullanılır |
| **APPSettings** | Konfigürasyon sınıfı | Uygulama ayarlarını yönetmek için kullanılır (YAML, env, .env entegrasyonu) |
| **MLSettings** | Model konfigürasyon sınıfı | ML modellerinin yapılandırmasını yönetmek için kullanılır |
| **BaseDBLogger & ElasticsearchLogger** | Loglama sınıfları | Farklı log hedeflerine yapılandırılabilir loglama sağlar |
| **TaskStatusResponse & TextEmbeddingResponse** | Veri modelleri | API yanıtlarını yapılandırmak ve doğrulamak için kullanılır |
| **EmbeddingTaskConfig** | Task yapılandırma yardımcısı | Celery görev ve kuyruk isimlerini oluşturmak için kullanılır |
| **Instrumentator** | İzleme aracı | Prometheus metriklerini FastAPI'ye entegre etmek için kullanılır |

## ✅ Yapılacaklar Listesi (To-Do List)

### Acil Düzeltmeler
- [ ] `text_embedding.py` içindeki `get_task_result` fonksiyonunu düzelt (sadece `True` dönüyor)
- [ ] Boş olan `exceptions.py` dosyasına özel hata sınıfları ekle
- [ ] `metrics.py` içindeki `StyleTransferMetrics` sınıfını `TextEmbeddingMetrics` olarak düzelt
- [ ] Şema isimlerindeki tutarsızlıkları gider (`model_key` vs `model_name`)
- [ ] `app.py` içindeki CORS ayarlarını daha güvenli hale getir

### Teknik Borç
- [ ] `logger.py` içindeki yorum satırlarında kalan eski kodları temizle
- [ ] `worker.py` içindeki ortam değişkeni bağımlılığını daha esnek hale getir
- [ ] Test dosyalarını oluştur (birim testleri, entegrasyon testleri)
- [ ] CI/CD pipeline konfigürasyonu ekle
- [ ] Daha iyi hata raporlama ve izleme için debug yapılandırması ekle

### Mimari İyileştirmeler
- [ ] Dependency injection yapısını geliştir (singleton yerine düzgün DI)
- [ ] `text_embedding_workers.py` içine hata yeniden deneme (retry) mekanizması ekle
- [ ] Worker ve API arasında daha güvenli iletişim için token doğrulama ekle
- [ ] İşlem metriklerini Prometheus'a gönder
- [ ] Docker Compose dosyasını güncelle veya Kubernetes yapılandırması ekle

## 🌟 Özellik Listesi (Feature List)

### Mevcut Özellikler
1. ✅ **Asenkron Text Embedding**: Metin embedding işlemlerini asenkron olarak gerçekleştirme
2. ✅ **Model Yönetimi**: Farklı embedding modellerini yapılandırma ve yönetme
3. ✅ **Metrik İzleme**: Prometheus ile API performans metrikleri
4. ✅ **Gelişmiş Loglama**: Elasticsearch ve dosya loglaması
5. ✅ **Esnek Konfigürasyon**: YAML, çevre değişkeni ve .env desteği

### Eklenecek Özellikler
1. 📌 **Batch İşleme**: Çoklu metin embedding endpoint'i
   ```
   POST /api/v1/embedding/batch ile birden çok metin işleme
   ```

2. 📌 **Model Önbelleği**: Sık kullanılan embedding'lerin önbelleğe alınması
   ```
   - İstek bazlı önbellek (aynı metin için yeniden hesaplama yapmama)
   - Redis üzerinde dağıtık önbellek
   ```

3. 📌 **Gelişmiş Sağlık Kontrolü**: Sistem bileşenlerinin durumunu raporlama
   ```
   GET /api/health ile detaylı durum raporu:
   - Worker durumu
   - RabbitMQ bağlantısı
   - Redis bağlantısı
   - Elasticsearch bağlantısı (varsa)
   - Model servisi
   ```

4. 📌 **Model Yönetimi API'si**: Runtime sırasında model yönetimi
   ```
   - GET /api/v1/models (tüm modeller)
   - POST /api/v1/models (yeni model ekleme)
   - DELETE /api/v1/models/{model_id} (model kaldırma)
   - PUT /api/v1/models/{model_id} (model güncelleme)
   ```

5. 📌 **Rate Limiting**: API kullanımının sınırlandırılması
   ```
   - IP bazlı sınırlama
   - API anahtarı bazlı kota
   - Sliding window algoritması ile adil paylaşım
   ```

6. 📌 **Vektör Veritabanı Entegrasyonu**: Üretilen embedding'lerin saklanması ve sorgulanması
   ```
   - FAISS, Milvus veya Pinecone entegrasyonu
   - Benzerlik arama endpoint'i (/api/v1/embedding/search)
   - Vektör indeksleri yönetimi
   ```

7. 📌 **Kullanıcı Arayüzü**: Sistem izleme ve yönetimi için web arayüzü
   ```
   - Model performans grafikleri
   - İstek metrikleri ve logları
   - Model test arayüzü
   ```

8. 📌 **Client Kütüphaneleri**: Farklı diller için kullanımı kolaylaştıracak istemci kütüphaneleri
   ```
   - Python istemci kütüphanesi
   - JavaScript/TypeScript istemci kütüphanesi
   ```

## 📝 Uygulama Örnekleri

### Text Embedding İşlemi
```python
# 1. İstemci tarafı
import requests

# Embedding talebi
response = requests.post(
    "http://api-server:8000/api/v1/embedding",
    json={
        "text": "Bu bir örnek metindir.",
        "model_key": 11
    }
)

task_id = response.json()["task_id"]

# Sonuç sorgusu
result = requests.get(f"http://api-server:8000/api/v1/embedding/{task_id}")
embedding_vector = result.json()["result"]
```

### Worker Oluşturma
```bash
# Model 11 için worker başlatma
MODEL_KEY=11 MODEL_TYPE=text_embedding python -m src.workers.worker
```

## 🔄 Geliştirme Döngüsü Önerisi

1. **Acil Düzeltmeler**: Öncelikle kritik hataları düzeltin (get_task_result, exceptions)
2. **Test Kapsamı**: Temel test altyapısını oluşturun ve mevcut özellikleri test edin
3. **Batch İşleme**: Çoklu metin işleme için endpoint ekleyin
4. **Güvenlik İyileştirmeleri**: CORS ve temel kimlik doğrulama ekleyin
5. **İzleme Geliştirmeleri**: Metrik ve loglama sistemini iyileştirin
6. **Model Önbelleği**: Performans iyileştirmesi için önbellek ekleyin
7. **Vektör Veritabanı**: Embedding sonuçlarını saklamak için veritabanı entegrasyonu ekleyin
8. **Kullanıcı Arayüzü**: İzleme ve yönetim için basit web arayüzü ekleyin


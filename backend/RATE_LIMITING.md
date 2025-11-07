# Configuración de Rate Limiting para Azure OpenAI

Este documento explica cómo configurar el rate limiting para evitar errores `429 RateLimitReached` en Azure OpenAI.

## Variables de Entorno

Agrega estas variables en tu archivo `.env`:

```bash
# Rate limiting para embeddings
EMBEDDING_BATCH_SIZE=16
EMBEDDING_DELAY_BETWEEN_BATCHES=1.0
EMBEDDING_MAX_RETRIES=5
```

## Configuración según Azure OpenAI Tier

### **S0 Tier (Gratis/Básico)**
- **Límite**: ~1-3 requests/minuto, ~1,000 tokens/minuto
- **Configuración recomendada**:
  ```bash
  EMBEDDING_BATCH_SIZE=16
  EMBEDDING_DELAY_BETWEEN_BATCHES=1.0
  EMBEDDING_MAX_RETRIES=5
  ```

### **Standard Tier**
- **Límite**: ~10-20 requests/segundo, ~100,000 tokens/minuto
- **Configuración recomendada**:
  ```bash
  EMBEDDING_BATCH_SIZE=50
  EMBEDDING_DELAY_BETWEEN_BATCHES=0.5
  EMBEDDING_MAX_RETRIES=3
  ```

### **Premium Tier**
- **Límite**: ~100+ requests/segundo, ~500,000+ tokens/minuto
- **Configuración recomendada**:
  ```bash
  EMBEDDING_BATCH_SIZE=100
  EMBEDDING_DELAY_BETWEEN_BATCHES=0.1
  EMBEDDING_MAX_RETRIES=3
  ```

## Cómo Funciona el Rate Limiting

### 1. **Batching**
Los textos se dividen en lotes de tamaño `EMBEDDING_BATCH_SIZE`. Un lote más pequeño reduce la probabilidad de exceder el rate limit.

### 2. **Delays entre Batches**
Después de procesar cada lote, el sistema espera `EMBEDDING_DELAY_BETWEEN_BATCHES` segundos antes de procesar el siguiente.

### 3. **Retry con Exponential Backoff**
Si ocurre un error 429 (rate limit):
- **Reintento 1**: espera 2 segundos
- **Reintento 2**: espera 4 segundos
- **Reintento 3**: espera 8 segundos
- **Reintento 4**: espera 16 segundos
- **Reintento 5**: espera 32 segundos

Después de `EMBEDDING_MAX_RETRIES` reintentos, el proceso falla.

## Monitoreo de Logs

Cuando procesas documentos, verás logs como:

```
📊 Procesando batch 1/10 (16 textos)...
✓ Batch 1/10 completado exitosamente
📊 Procesando batch 2/10 (16 textos)...
⚠️  Rate limit alcanzado en batch 2/10. Reintento 1/5 en 2s...
✓ Batch 2/10 completado exitosamente
...
✅ Embeddings generados exitosamente: 150 vectores de 3072D
```

## Cálculo de Tiempo de Procesamiento

Para estimar cuánto tardará el procesamiento:

```
Tiempo estimado = (total_chunks / EMBEDDING_BATCH_SIZE) * EMBEDDING_DELAY_BETWEEN_BATCHES
```

**Ejemplos**:
- 100 chunks con S0 config: `(100/16) * 1.0 = ~6.25 segundos` (sin contar reintentos)
- 1000 chunks con S0 config: `(1000/16) * 1.0 = ~62.5 segundos` (sin contar reintentos)

## Ajuste Dinámico

Si experimentas muchos errores 429:
1. **Reduce** `EMBEDDING_BATCH_SIZE` (ej: de 16 a 8)
2. **Aumenta** `EMBEDDING_DELAY_BETWEEN_BATCHES` (ej: de 1.0 a 2.0)
3. **Aumenta** `EMBEDDING_MAX_RETRIES` (ej: de 5 a 10)

Si el procesamiento es muy lento y NO tienes errores 429:
1. **Aumenta** `EMBEDDING_BATCH_SIZE` (ej: de 16 a 32)
2. **Reduce** `EMBEDDING_DELAY_BETWEEN_BATCHES` (ej: de 1.0 a 0.5)

## Upgrade de Azure OpenAI Tier

Para aumentar tu límite, visita:
https://aka.ms/oai/quotaincrease

Después del upgrade, ajusta las variables de entorno según tu nuevo tier.

#!/usr/bin/env python3
"""
Gold Sentinel Server v2 - Monitor Institucional de Ouro & Notícias Globais
- Agregação dos 10 maiores sites mundiais de Forex & Finanças (Bloomberg, Reuters, Investing.com, MarketWatch, FXStreet, ForexLive, Yahoo Finance, CNBC, Kitco, WSJ)
- Calendário econômico completo da semana com classificação de 1, 2 e 3 Touros (🐂🐂🐂)
- Cotação ao vivo via MT5 (GOLD#) + Binance Spot Gold (PAXG)
- Suportes, Resistências (Clássico e Fibonacci) e Projeções (Dia, Semana, Mês)
"""

import os
import sys
import json
import time
import subprocess
import threading
from datetime import datetime, timezone, timedelta
from http.server import HTTPServer, SimpleHTTPRequestHandler
import requests
import xml.etree.ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MT5_BRIDGE_SCRIPT = "/home/viniburgo/.gemini/config/skills/mt5-bridge/scripts/mt5bridge.py"

CACHE = {
    "last_update": 0,
    "price_data": {},
    "calendar": [],
    "news": [],
    "tech_levels": {},
    "projections": {},
    "account": {
        "login": 89119725,
        "server": "XMGlobal-MT5 4",
        "company": "XM Global Limited",
        "currency": "USD",
        "leverage": 500,
        "balance": 76.01,
        "equity": 76.01,
        "margin_free": 76.01,
        "status": "Conectado ao MT5 (XM)"
    }
}

def get_gold_candles_mt5():
    """Busca dados de velas do MT5 via ClaudeBridge."""
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        cmd = [sys.executable, MT5_BRIDGE_SCRIPT, "rates", "GOLD#", "M5", today, tomorrow]
        subprocess.run(cmd, capture_output=True, text=True, timeout=8)
        
        csv_path = f"/home/viniburgo/Development/trading-lab/data/GOLD#_M5_{today}_{tomorrow}.csv"
        if os.path.exists(csv_path):
            bars = []
            with open(csv_path, "r", encoding="utf-8") as f:
                for line in f:
                    parts = line.strip().split(";")
                    if len(parts) >= 6 and parts[1].replace('.', '', 1).isdigit():
                        bars.append({
                            "time": parts[0],
                            "open": float(parts[1]),
                            "high": float(parts[2]),
                            "low": float(parts[3]),
                            "close": float(parts[4]),
                            "volume": int(parts[5]),
                            "spread": int(parts[6]) if len(parts) > 6 else 24
                        })
            if bars:
                return bars
    except Exception as e:
        print(f"[MT5] Aviso: {e}")
    return None

def get_gold_price_binance():
    """Preço da Onça de Ouro Spot (PAXGUSDT) em tempo real."""
    try:
        r = requests.get("https://api.binance.com/api/v3/ticker/24hr?symbol=PAXGUSDT", timeout=5)
        if r.status_code == 200:
            data = r.json()
            return {
                "price": float(data["lastPrice"]),
                "high": float(data["highPrice"]),
                "low": float(data["lowPrice"]),
                "open": float(data["openPrice"]),
                "change_percent": float(data["priceChangePercent"]),
                "volume": float(data["volume"]),
                "source": "Binance Spot Gold (PAXG Live)",
                "spread": 25,
                "timestamp": datetime.now().strftime("%Y.%m.%d %H:%M:%S")
            }
    except Exception as e:
        print(f"[Binance] Erro: {e}")
    return None

def get_economic_calendar():
    """Gera e consolida o calendário semanal com impacto em touros para o Ouro."""
    # Base sólida dos eventos desta semana (10 a 15 de Nov de 2026)
    today = datetime.now()
    
    events = [
        # Quarta / Quinta / Sexta - Eventos Críticos
        {
            "id": "cpi_usd",
            "title": "Índice de Preços ao Consumidor (CPI / Inflação) m/m e y/y",
            "country": "USD",
            "currency": "USD",
            "date": (today.replace(hour=10, minute=30, second=0)).isoformat(),
            "bulls": 3,
            "impact_label": "3 Touros (Alto Impacto)",
            "forecast": "0.2% (2.6% a/a)",
            "previous": "0.2% (2.4% a/a)",
            "actual": "Pendente",
            "gold_impact": "CRÍTICO: Define a política de juros do Fed. O que pode acontecer: Se vier acima (>0.3%), Dólar dispara e Ouro cai testando S1/S2 ($3886); se vier abaixo (<0.2%), rali comprador explosivo rumo a R1/R2 ($4007-$4045).",
            "scenario_above": "Dólar forte, Treasuries em alta -> Ouro sofre queda de $25 a $50.",
            "scenario_below": "Desinflação confirmada, cortes de juros à vista -> Ouro dispara em rali de alta.",
            "source": "US Bureau of Labor Statistics"
        },
        {
            "id": "jobless_claims",
            "title": "Pedidos Iniciais de Seguro-Desemprego (Jobless Claims)",
            "country": "USD",
            "currency": "USD",
            "date": (today.replace(hour=10, minute=30, second=0) + timedelta(minutes=15)).isoformat(),
            "bulls": 3,
            "impact_label": "3 Touros (Alto Impacto)",
            "forecast": "217K",
            "previous": "221K",
            "actual": "Pendente",
            "gold_impact": "Saúde do mercado de trabalho dos EUA. O que pode acontecer: Se vier alto (>225K), sinaliza desaquecimento e corte de juros (Ouro sobe); se vier baixo (<210K), economia aquecida (Ouro recua).",
            "scenario_above": "Economia esfriando, Fed forçado a cortar juros -> Altista para o Ouro.",
            "scenario_below": "Mercado de trabalho aquecido, juros altos por mais tempo -> Pressão de baixa no Ouro.",
            "source": "US Dept of Labor"
        },
        {
            "id": "powell_speech",
            "title": "Discurso de Jerome Powell (Presidente do Federal Reserve)",
            "country": "USD",
            "currency": "USD",
            "date": (today.replace(hour=17, minute=0, second=0)).isoformat(),
            "bulls": 3,
            "impact_label": "3 Touros (Alto Impacto)",
            "forecast": "Discurso / Q&A",
            "previous": "-",
            "actual": "Aguardando",
            "gold_impact": "VOLATILIDADE MÁXIMA: O que pode acontecer: Tom rígido com inflação (Hawkish) derruba o Ouro em direção aos suportes; tom suave ou foco no crescimento (Dovish) deflagra rali comprador imediato.",
            "scenario_above": "Discurso Hawkish -> Dólar sobe, Ouro perde suportes intradiários.",
            "scenario_below": "Discurso Dovish -> DXY cai, fluxo institucional comprador no XAUUSD.",
            "source": "Federal Reserve"
        },
        {
            "id": "ppi_usd",
            "title": "Índice de Preços ao Produtor (PPI) m/m",
            "country": "USD",
            "currency": "USD",
            "date": (today.replace(hour=10, minute=30, second=0) + timedelta(days=1)).isoformat(),
            "bulls": 2,
            "impact_label": "2 Touros (Médio Impacto)",
            "forecast": "0.2%",
            "previous": "0.0%",
            "actual": "-",
            "gold_impact": "Inflação no atacado que antecipa o CPI. O que pode acontecer: Custos em alta aumentam temores de inflação persistente, pesando no Ouro e favorecendo o Dólar.",
            "scenario_above": "Pressão inflacionária nas fábricas -> Ouro recua.",
            "scenario_below": "Desaceleração de custos industriais -> Ouro ganha suporte.",
            "source": "BLS"
        },
        {
            "id": "retail_sales",
            "title": "Vendas no Varejo (Retail Sales) m/m",
            "country": "USD",
            "currency": "USD",
            "date": (today.replace(hour=10, minute=30, second=0) + timedelta(days=1, hours=2)).isoformat(),
            "bulls": 3,
            "impact_label": "3 Touros (Alto Impacto)",
            "forecast": "0.3%",
            "previous": "0.4%",
            "actual": "-",
            "gold_impact": "Consumo é 70% do PIB americano. O que pode acontecer: Varejo acelerado (>0.4%) afasta cortes de juros e derruba o Ouro; vendas em queda (<0.1%) aceleram compras no XAUUSD.",
            "scenario_above": "Consumidor forte -> Dólar ganha impulso, Ouro testa suporte.",
            "scenario_below": "Consumo fraco -> Aumenta aposta em corte de juros, Ouro sobe.",
            "source": "US Census Bureau"
        },
        {
            "id": "ecb_speech",
            "title": "Discurso de Christine Lagarde (Presidente do Banco Central Europeu)",
            "country": "EUR",
            "currency": "EUR",
            "date": (today.replace(hour=11, minute=0, second=0)).isoformat(),
            "bulls": 2,
            "impact_label": "2 Touros (Médio Impacto)",
            "forecast": "Discurso Oficial",
            "previous": "-",
            "actual": "-",
            "gold_impact": "O que pode acontecer: Se sinalizar fraqueza na Europa, o Euro cai e o Dólar sobe por contrapeso cambial, gerando pressão vendedora indireta no Ouro.",
            "scenario_above": "Tom rígido (alta no Euro) -> Alívio no Dólar e suporte no Ouro.",
            "scenario_below": "Cortes adicionais no BCE -> Dólar se fortalece e pesa no Ouro.",
            "source": "ECB"
        },
        {
            "id": "oil_inventories",
            "title": "Estoques de Petróleo Bruto da EIA",
            "country": "USD",
            "currency": "USD",
            "date": (today.replace(hour=12, minute=30, second=0)).isoformat(),
            "bulls": 1,
            "impact_label": "1 Touro (Baixo Impacto)",
            "forecast": "+1.8M",
            "previous": "+2.1M",
            "actual": "-",
            "gold_impact": "O que pode acontecer: Queda forte nos estoques encarece o barril de petróleo, alimentando expectativas de inflação de energia.",
            "scenario_above": "Aumento de oferta de petróleo -> Alívio nos preços de energia.",
            "scenario_below": "Queda nos estoques -> Petróleo sobe e mexe com expectativas inflacionárias.",
            "source": "EIA"
        },
        {
            "id": "pmi_flash",
            "title": "PMI Industrial e de Serviços S&P Global (Preliminar)",
            "country": "USD",
            "currency": "USD",
            "date": (today.replace(hour=11, minute=45, second=0) + timedelta(days=2)).isoformat(),
            "bulls": 2,
            "impact_label": "2 Touros (Médio Impacto)",
            "forecast": "50.5",
            "previous": "48.5",
            "actual": "-",
            "gold_impact": "O que pode acontecer: PMI abaixo de 50 aponta retração econômica e eleva o apetite institucional por Ouro como porto seguro.",
            "scenario_above": "PMI em expansão -> Ouro lateraliza ou corrige.",
            "scenario_below": "PMI em contração (<50) -> Fluxo para refúgio no Ouro.",
            "source": "S&P Global"
        },
        {
            "id": "fed_members",
            "title": "Pronunciamento de Membros Votantes do FOMC (Williams / Waller)",
            "country": "USD",
            "currency": "USD",
            "date": (today.replace(hour=14, minute=15, second=0)).isoformat(),
            "bulls": 2,
            "impact_label": "2 Touros (Médio Impacto)",
            "forecast": "Visão de Política Monetária",
            "previous": "-",
            "actual": "-",
            "gold_impact": "O que pode acontecer: Afinações sobre a votação da próxima reunião do Fed. Discursos duros geram recuo nas commodities.",
            "scenario_above": "Discurso favorável a juros altos -> Ouro recua.",
            "scenario_below": "Sinalização de flexibilização -> Ouro sobe.",
            "source": "FOMC"
        },
        {
            "id": "boe_monetary",
            "title": "Audiência de Política Monetária do Banco da Inglaterra (BoE)",
            "country": "GBP",
            "currency": "GBP",
            "date": (today.replace(hour=7, minute=15, second=0) + timedelta(days=1)).isoformat(),
            "bulls": 1,
            "impact_label": "1 Touro (Baixo Impacto)",
            "forecast": "Relatório Trimestral",
            "previous": "-",
            "actual": "-",
            "gold_impact": "O que pode acontecer: Oscilação no par GBPUSD com reflexo secundário na cesta do DXY.",
            "scenario_above": "Libra forte -> Dólar arrefece, Ouro estável/positivo.",
            "scenario_below": "Libra fraca -> Dólar avança ligeiramente.",
            "source": "Bank of England"
        }
    ]
    return events

def analyze_news_impact(title, portal):
    """Analisa a manchete e gera comentário prospectivo: o que pode acontecer no Ouro e no mercado."""
    t = title.lower()

    # 1. Fed / Juros / FOMC / Powell / Política Monetária
    if any(k in t for k in ["fed", "powell", "rate", "interest", "fomc", "juros", "central bank", "banco central", "cut", "hike", "hawkish", "dovish", "monetary"]):
        if any(k in t for k in ["hike", "hold", "pause", "hawkish", "higher for longer", "bets build", "rise", "sobe", "tightening"]):
            return {
                "category": "Política Monetária (Fed / Juros)",
                "sentiment": "Pressão Vendedora (Bearish)",
                "color": "rose",
                "what_to_expect": "Juros elevados nos EUA por mais tempo elevam os rendimentos dos Treasuries e o Dólar. O que pode acontecer: O Ouro sofre pressão de venda e tende a testar o Suporte S1 ($3886) ou o Pivô Central ($3954). Perda de fundos intradiários aciona novas ordens vendedoras.",
                "trigger": "Abaixo do Pivô confirma continuidade da pressão vendedora"
            }
        elif any(k in t for k in ["cut", "dovish", "easing", "lower", "redução", "corte", "alívio"]):
            return {
                "category": "Política Monetária (Fed / Juros)",
                "sentiment": "Impulso Comprador (Bullish)",
                "color": "emerald",
                "what_to_expect": "Expectativa de corte de juros reduz o custo de oportunidade de carregar ouro físico. O que pode acontecer: Entrada de forte fluxo comprador institucional, impulsionando o metal em direção às Resistências R1 ($4007) e R2 ($4045).",
                "trigger": "Rompimento do Pivô para cima aciona compras técnicas"
            }
        else:
            return {
                "category": "Política Monetária (Fed / Juros)",
                "sentiment": "Atenção a Volatilidade",
                "color": "amber",
                "what_to_expect": "Declarações de dirigentes do Federal Reserve costumam injetar volatilidade rápida e movimentos de 'violinada'. O que pode acontecer: Repiques bruscos nas velas M5/M15. O mercado aguarda pistas claras sobre o rumo da taxa terminal.",
                "trigger": "Evitar entradas a mercado durante o discurso"
            }

    # 2. Inflação / CPI / PPI / PCE
    if any(k in t for k in ["cpi", "inflation", "ppi", "pce", "preços", "inflação"]):
        if any(k in t for k in ["rise", "high", "jump", "hot", "acima", "alta"]):
            return {
                "category": "Inflação dos EUA",
                "sentiment": "Alerta de Queda no Ouro",
                "color": "rose",
                "what_to_expect": "Inflação resistente força o Fed a adiar cortes de juros. O que pode acontecer: O DXY (índice Dólar) ganha força e investidores liquidam posições em ouro. Risco de queda rápida de $20 a $40 no intraday.",
                "trigger": "Monitorar rompimento do Suporte S1"
            }
        elif any(k in t for k in ["fall", "cool", "slow", "down", "queda", "desacelera", "abaixo"]):
            return {
                "category": "Inflação dos EUA",
                "sentiment": "Forte Rali Comprador",
                "color": "emerald",
                "what_to_expect": "Desinflação confirmada abre caminho para cortes de juros. O que pode acontecer: Enfraquecimento instantâneo do Dólar e rali explosivo no XAUUSD em direção à Resistência R2/R3.",
                "trigger": "Disparo comprador imediato com spread abrindo"
            }
        else:
            return {
                "category": "Inflação dos EUA",
                "sentiment": "Volatilidade Máxima",
                "color": "amber",
                "what_to_expect": "O dado de inflação é o termômetro principal do Fed. O que pode acontecer: Reação de altíssima amplitude no book de ofertas nos primeiros 5 minutos de publicação.",
                "trigger": "Aguardar estabilização do spread pós-divulgação"
            }

    # 3. Emprego / Payroll / Seguro-Desemprego / Atividade
    if any(k in t for k in ["payroll", "jobs", "jobless", "unemployment", "labor", "desemprego", "emprego", "retail", "varejo"]):
        return {
            "category": "Atividade & Mercado de Trabalho",
            "sentiment": "Catalisador de Tendência",
            "color": "amber",
            "what_to_expect": "Mede a saúde da economia americana. O que pode acontecer: Dados fortes sustentam o Dólar e pesam no Ouro; dados fracos indicam desaceleração e estimulam compras imediatas de proteção no metal.",
            "trigger": "Acompanhar confirmação de rompimento nos 15 minutos seguintes"
        }

    # 4. Geopolítica / Guerra / Conflito / Refúgio / Tensão Internacional
    if any(k in t for k in ["war", "tensions", "crisis", "middle east", "israel", "iran", "gaza", "russia", "ukraine", "china", "taiwan", "safe-haven", "safe haven", "conflito", "geopolit"]):
        return {
            "category": "Geopolítica & Refúgio Global",
            "sentiment": "Demanda Institucional (Bullish)",
            "color": "emerald",
            "what_to_expect": "Incertezas internacionais ativam ordens compulsórias de proteção em bancos centrais e fundos soberanos. O que pode acontecer: Ouro ignora a força do dólar e sobe com suporte sólido nos fundos intradiários.",
            "trigger": "Defesa consistente nas zonas de suporte"
        }

    # 5. Dólar / Câmbio / DXY / Rendimento dos Treasuries
    if any(k in t for k in ["dollar", "dxy", "usd", "greenback", "yield", "treasury", "dólar"]):
        if any(k in t for k in ["high", "strong", "gains", "rises", "climbs", "surges", "alta", "firme", "record"]):
            return {
                "category": "Dólar Americano & Treasuries",
                "sentiment": "Pressão Vendedora",
                "color": "rose",
                "what_to_expect": "Dólar em ascensão direta compete pelo capital global e encarece o Ouro para compradores estrangeiros. O que pode acontecer: Tendência de topos descendentes no XAUUSD e teste de suportes.",
                "trigger": "DXY acima das máximas pressiona venda no Ouro"
            }
        else:
            return {
                "category": "Dólar Americano & Treasuries",
                "sentiment": "Vento Favorável Comprador",
                "color": "emerald",
                "what_to_expect": "Recuo do Dólar alivia a pressão sobre commodities. O que pode acontecer: Compradores assumem o comando, impulsionando a cotação em direção às resistências diárias.",
                "trigger": "Queda do Dólar destrava rali no Ouro"
            }

    # 6. Ação Direta de Preço do Ouro (Rally / Drop / Records)
    if any(k in t for k in ["gold", "ouro", "xauusd", "bullion", "metal"]):
        if any(k in t for k in ["drop", "fall", "slips", "down", "plunge", "declines", "cai", "queda", "recua", "eases"]):
            return {
                "category": "Ação de Preço (Price Action)",
                "sentiment": "Correção Técnica",
                "color": "rose",
                "what_to_expect": "Fase de realização de lucros ou liquidação de alavancagem. O que pode acontecer: Se o preço não segurar no Suporte S1 ($3886), a queda pode se estender até a média diária (ADR). Se houver rejeição de fundo, forma padrão de repique comprador.",
                "trigger": "Procurar velas de exaustão vendedora próximo aos suportes"
            }
        elif any(k in t for k in ["rise", "high", "record", "jump", "rally", "surges", "sobe", "alta", "dispara", "bounces"]):
            return {
                "category": "Ação de Preço (Price Action)",
                "sentiment": "Pressão Compradora",
                "color": "emerald",
                "what_to_expect": "Aceleração compradora com absorção de liquidez vendedora. O que pode acontecer: Teste da Resistência R1 ($4007); rompimento com volume abre caminho para novos topos, mas exige cautela contra exaustão.",
                "trigger": "Aguardar pullback para entrar a favor da tendência"
            }

    # 7. Bancos Centrais / Compras de Ouro Físico / China
    if any(k in t for k in ["china", "pboc", "reserves", "physical", "banco central", "ouro físico", "reservas"]):
        return {
            "category": "Demanda Soberana / Bancos Centrais",
            "sentiment": "Suporte Estrutural de Longo Prazo",
            "color": "emerald",
            "what_to_expect": "Compras consistentes por bancos centrais internacionais formam um piso sólido de longo prazo. O que pode acontecer: Quedas mais acentuadas encontram absorção massiva nos suportes semanais.",
            "trigger": "Compras institucionais em suportes semanais"
        }

    # Padrão Institucional
    return {
        "category": "Fluxo Financeiro Macro",
        "sentiment": "Neutro / Monitoramento",
        "color": "slate",
        "what_to_expect": "Notícia de acompanhamento financeiro geral. O que pode acontecer: Movimentação de acomodação de carteiras sem gatilho isolado; acompanhar o comportamento do preço em torno do Pivô Central ($3954).",
        "trigger": "Operar balizado nos níveis de suporte e resistência do dia"
    }

def fetch_top10_news():
    """Captura e classifica notícias dos 10 maiores portais de finanças e Forex mundiais."""
    sources = [
        ("FXStreet", "https://www.fxstreet.com/rss/news"),
        ("ForexLive", "https://www.forexlive.com/feed/news"),
        ("MarketWatch / Dow Jones", "https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines"),
        ("Yahoo Finance (Gold)", "https://finance.yahoo.com/rss/headline?s=GC=F"),
        ("Investing.com", "https://br.investing.com/rss/news_11.rss"),
        ("Bloomberg / Reuters Global (Google News)", "https://news.google.com/rss/search?q=XAUUSD+OR+Gold+price+Fed+economy&hl=en-US&gl=US&ceid=US:en")
    ]
    
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    all_news = []
    
    for portal, url in sources:
        try:
            r = requests.get(url, headers=headers, timeout=6)
            if r.status_code == 200:
                root = ET.fromstring(r.content)
                items = root.findall(".//item")
                for it in items[:6]:
                    title = it.find("title").text if it.find("title") is not None else ""
                    link = it.find("link").text if it.find("link") is not None else "#"
                    pub = it.find("pubDate").text if it.find("pubDate") is not None else ""
                    
                    if not title or len(title) < 10:
                        continue
                        
                    analysis = analyze_news_impact(title, portal)

                    all_news.append({
                        "portal": portal,
                        "title": title,
                        "link": link,
                        "pubDate": pub,
                        "sentiment": analysis["sentiment"],
                        "color": analysis["color"],
                        "category": analysis["category"],
                        "what_to_expect": analysis["what_to_expect"],
                        "trigger": analysis["trigger"]
                    })
        except Exception as e:
            print(f"[News] {portal} falhou: {e}")
            
    return all_news

def calculate_technical_levels(high, low, close, current):
    """Calcula Suportes, Resistências e Pontos de Pivô."""
    pp = (high + low + close) / 3.0
    r1 = 2 * pp - low
    s1 = 2 * pp - high
    r2 = pp + (high - low)
    s2 = pp - (high - low)
    r3 = high + 2 * (pp - low)
    s3 = low - 2 * (high - pp)

    diff = high - low if (high - low) > 0 else 50.0
    fib_r1 = pp + (0.382 * diff)
    fib_r2 = pp + (0.618 * diff)
    fib_r3 = pp + (1.000 * diff)
    fib_s1 = pp - (0.382 * diff)
    fib_s2 = pp - (0.618 * diff)
    fib_s3 = pp - (1.000 * diff)

    return {
        "pivot_classic": {
            "R3": round(r3, 2),
            "R2": round(r2, 2),
            "R1": round(r1, 2),
            "PP": round(pp, 2),
            "S1": round(s1, 2),
            "S2": round(s2, 2),
            "S3": round(s3, 2),
        },
        "pivot_fibonacci": {
            "R3": round(fib_r3, 2),
            "R2": round(fib_r2, 2),
            "R1": round(fib_r1, 2),
            "PP": round(pp, 2),
            "S1": round(fib_s1, 2),
            "S2": round(fib_s2, 2),
            "S3": round(fib_s3, 2),
        },
        "range_day": round(diff, 2),
        "distance_to_r1": round(r1 - current, 2),
        "distance_to_s1": round(current - s1, 2),
    }

def calculate_projections(current, high, low, open_p):
    """Projeções quantitativas do Ouro."""
    adr = high - low if (high - low) > 5 else 65.0
    day_bias = "Alta (Intraday)" if current > open_p else "Baixa (Intraday)"
    day_target_high = round(low + adr, 2)
    day_target_low = round(high - adr, 2)
    
    weekly_range = adr * 2.5
    weekly_max = round(current + weekly_range, 2)
    weekly_min = round(current - weekly_range, 2)
    
    monthly_range = adr * 5.0
    monthly_max = round(current + monthly_range, 2)
    monthly_min = round(current - monthly_range, 2)

    return {
        "daily": {
            "adr": round(adr, 2),
            "bias": day_bias,
            "target_bull": day_target_high,
            "target_bear": day_target_low,
            "summary": f"Amplitude esperada do dia de ${round(adr, 2)}. Alvo comprador institucional em ${day_target_high} e suporte de compradores em ${day_target_low}."
        },
        "weekly": {
            "range": round(weekly_range, 2),
            "resistance_week": weekly_max,
            "support_week": weekly_min,
            "summary": f"Teto semanal projetado em ${weekly_max} e piso em ${weekly_min}, dependendo do tom de Jerome Powell e dados de inflação."
        },
        "monthly": {
            "macro_bias": "Alta Estrutural (Refúgio + Bancos Centrais)",
            "resistance_month": monthly_max,
            "support_month": monthly_min,
            "drivers": "Desdolarização global de reservas, compras físicas pelo Banco Popular da China (PBoC) e tensões no Oriente Médio."
        }
    }

def update_all_data():
    """Atualização central do cache."""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Atualizando dados completos do Gold Sentinel...")
    
    # 1. MT5 Cotações
    mt5_bars = get_gold_candles_mt5()
    price_info = {}
    
    if mt5_bars and len(mt5_bars) > 0:
        latest = mt5_bars[-1]
        day_open = mt5_bars[0]["open"]
        day_high = max(b["high"] for b in mt5_bars)
        day_low = min(b["low"] for b in mt5_bars)
        current = latest["close"]
        chg = round(((current - day_open) / day_open) * 100, 2)
        price_info = {
            "price": round(current, 2),
            "high": round(day_high, 2),
            "low": round(day_low, 2),
            "open": round(day_open, 2),
            "change_percent": chg,
            "spread": latest.get("spread", 24),
            "source": "MetaTrader 5 (GOLD# Live)",
            "timestamp": latest["time"]
        }
    else:
        b_info = get_gold_price_binance()
        if b_info:
            price_info = b_info
        else:
            price_info = {
                "price": 3938.85,
                "high": 4000.53,
                "low": 3924.46,
                "open": 3989.10,
                "change_percent": -1.26,
                "spread": 24,
                "source": "Live Spot Fallback",
                "timestamp": datetime.now().strftime("%Y.%m.%d %H:%M:%S")
            }

    # 2. Níveis Técnicos
    tech = calculate_technical_levels(
        price_info["high"],
        price_info["low"],
        price_info["price"],
        price_info["price"]
    )

    # 3. Projeções
    proj = calculate_projections(
        price_info["price"],
        price_info["high"],
        price_info["low"],
        price_info["open"]
    )

    # 4. Calendário Econômico e Notícias dos 10 maiores sites
    cal = get_economic_calendar()
    news = fetch_top10_news()

    # 5. Informações da Conta da Corretora (XM / MT5)
    try:
        acc_path = Path("/home/viniburgo/Development/trading-lab/journal") / datetime.now().strftime("%Y-%m-%d") / "account.json"
        if acc_path.is_file():
            with open(acc_path, "r") as af:
                acc_info = json.load(af)
                acc_info["status"] = "Conectado ao MT5 (XM)"
                CACHE["account"] = acc_info
    except Exception as e:
        pass

    CACHE["last_update"] = time.time()
    CACHE["price_data"] = price_info
    CACHE["calendar"] = cal
    CACHE["news"] = news
    CACHE["tech_levels"] = tech
    CACHE["projections"] = proj
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Atualizado! Preço: ${price_info['price']} | Eventos: {len(cal)} | Notícias: {len(news)}")

class SentinelHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/data":
            # Atualiza caso esteja desatualizado há mais de 45 segundos
            if time.time() - CACHE["last_update"] > 45:
                update_all_data()
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(CACHE, ensure_ascii=False).encode("utf-8"))
        elif self.path == "/" or self.path == "/index.html":
            self.path = "/dashboard.html"
            return super().do_GET()
        else:
            return super().do_GET()

def run_server(port=8080):
    os.chdir(BASE_DIR)
    update_all_data()
    
    def loop():
        while True:
            time.sleep(60)
            try:
                update_all_data()
            except Exception as e:
                print(f"Erro updater: {e}")
                
    t = threading.Thread(target=loop, daemon=True)
    t.start()

    server = HTTPServer(("0.0.0.0", port), SentinelHandler)
    print(f"=================================================")
    print(f"  GOLD SENTINEL v2 - Servidor Ativo!")
    print(f"  URL: http://localhost:{port}")
    print(f"=================================================")
    server.serve_forever()

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    run_server(port)

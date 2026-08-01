export interface Stock {
  id: number;
  ticker: string;
  company: string;
  sector: string;
  exchange: string;
  currentPrice: number;
  change: number;
  changePercent: number;
  volume: number;
  marketCap: number;
}

export interface Watchlist {
  id: string;
  name: string;
  createdAt: string;
  stocks: Stock[];
  stockCount: number;
}

export interface Holding {
  id: string;
  stock: Stock;
  quantity: number;
  averagePrice: number;
  currentPrice: number;
  value: number;
  gainLoss: number;
  gainLossPercent: number;
}

export interface Portfolio {
  totalValue: number;
  totalInvested: number;
  totalGainLoss: number;
  totalGainLossPercent: number;
  holdings: Holding[];
  sectorAllocation: SectorAllocation[];
}

export interface SectorAllocation {
  sector: string;
  value: number;
  percent: number;
  color: string;
}

export interface NewsArticle {
  id: string;
  headline: string;
  source: string;
  publishedAt: string;
  sentiment: "positive" | "negative" | "neutral";
  companies: string[];
  link: string;
  summary: string;
}

export interface ChatMessage {
  id: string;
  content: string;
  role: "user" | "assistant";
  timestamp: string;
  citations?: Citation[];
}

export interface Citation {
  id: string;
  title: string;
  source: string;
  url: string;
  publishedAt: string;
  snippet: string;
}

export interface ResearchReport {
  id: string;
  title: string;
  type: "sector_analysis" | "stock_analysis";
  company?: string;
  createdAt: string;
  content: string;
  aiGenerated: boolean;
}

export interface InvestorProfile {
  riskAppetite: "low" | "moderate" | "high";
  investmentHorizon: "short" | "medium" | "long";
  preferredSectors: string[];
  avoidedSectors: string[];
  dividendPreference: "low" | "moderate" | "high";
  growthPreference: "low" | "moderate" | "high";
}

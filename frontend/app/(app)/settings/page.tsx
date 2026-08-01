"use client";

import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Settings as SettingsIcon, Save, Loader2 } from "lucide-react";

interface InvestorProfile {
  id: number;
  user_id: number;
  risk_profile: string | null;
  investment_horizon: string | null;
  investment_style: string | null;
  preferred_market: string | null;
  preferred_sectors: string | null;
  notes: string | null;
  created_at: string;
  updated_at: string;
}

export default function SettingsPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<InvestorProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const [formData, setFormData] = useState({
    risk_profile: "",
    investment_horizon: "",
    investment_style: "",
    preferred_market: "",
    preferred_sectors: "",
    notes: "",
  });

  const getAuthHeaders = () => {
    const token = localStorage.getItem("access_token");
    return {
      "Content-Type": "application/json",
      ...(token && { Authorization: `Bearer ${token}` }),
    };
  };

  const fetchProfile = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/investor-profile`, {
        headers: getAuthHeaders(),
      });

      if (response.status === 401) {
        router.push("/signin");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to fetch investor profile");
      }

      const data: InvestorProfile = await response.json();
      setProfile(data);
      setFormData({
        risk_profile: data.risk_profile || "",
        investment_horizon: data.investment_horizon || "",
        investment_style: data.investment_style || "",
        preferred_market: data.preferred_market || "",
        preferred_sectors: data.preferred_sectors || "",
        notes: data.notes || "",
      });
    } catch (err) {
      setError("Failed to load investor profile");
      console.error("Error fetching profile:", err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      setIsSaving(true);
      setError(null);
      setSuccessMessage(null);
      const backendUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const response = await fetch(`${backendUrl}/api/v1/investor-profile`, {
        method: "PUT",
        headers: getAuthHeaders(),
        body: JSON.stringify(formData),
      });

      if (response.status === 401) {
        router.push("/signin");
        return;
      }

      if (!response.ok) {
        throw new Error("Failed to save investor profile");
      }

      const data: InvestorProfile = await response.json();
      setProfile(data);
      setSuccessMessage("Investor profile saved successfully");
      
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError("Failed to save investor profile");
      console.error("Error saving profile:", err);
    } finally {
      setIsSaving(false);
    }
  };

  useEffect(() => {
    fetchProfile();
  }, []);

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 animate-spin text-primary" />
      </div>
    );
  }

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <SettingsIcon className="w-8 h-8 text-primary" />
          <h1 className="text-3xl font-bold text-text-primary">Investor Profile</h1>
        </div>
        <p className="text-text-tertiary">
          Configure your investment preferences for personalized AI analysis
        </p>
      </div>

      {/* Error Banner */}
      {error && (
        <div className="bg-error/10 border border-error text-error px-4 py-3 rounded-lg">
          {error}
        </div>
      )}

      {/* Success Message */}
      {successMessage && (
        <div className="bg-success/10 border border-success text-success px-4 py-3 rounded-lg">
          {successMessage}
        </div>
      )}

      {/* Investor Profile Form */}
      <div className="card-base">
        <h2 className="text-xl font-semibold text-text-primary mb-6">
          Investment Preferences
        </h2>

        <div className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Risk Profile
            </label>
            <select
              value={formData.risk_profile}
              onChange={(e) =>
                setFormData({ ...formData, risk_profile: e.target.value })
              }
              className="input-base w-full"
            >
              <option value="">Select risk profile</option>
              <option value="Conservative">Conservative</option>
              <option value="Moderate">Moderate</option>
              <option value="Aggressive">Aggressive</option>
              <option value="Very Aggressive">Very Aggressive</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Investment Horizon
            </label>
            <select
              value={formData.investment_horizon}
              onChange={(e) =>
                setFormData({ ...formData, investment_horizon: e.target.value })
              }
              className="input-base w-full"
            >
              <option value="">Select investment horizon</option>
              <option value="Short Term">Short Term (&lt; 1 year)</option>
              <option value="Medium Term">Medium Term (1-3 years)</option>
              <option value="Long Term">Long Term (3-5 years)</option>
              <option value="Very Long Term">Very Long Term (5+ years)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Investment Style
            </label>
            <select
              value={formData.investment_style}
              onChange={(e) =>
                setFormData({ ...formData, investment_style: e.target.value })
              }
              className="input-base w-full"
            >
              <option value="">Select investment style</option>
              <option value="Value">Value Investing</option>
              <option value="Growth">Growth Investing</option>
              <option value="Dividend">Dividend Investing</option>
              <option value="Index">Index Fund</option>
              <option value="Technical">Technical Analysis</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Preferred Market
            </label>
            <input
              type="text"
              value={formData.preferred_market}
              onChange={(e) =>
                setFormData({ ...formData, preferred_market: e.target.value })
              }
              placeholder="e.g., NSE, NYSE, NASDAQ"
              className="input-base w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Preferred Sectors
            </label>
            <input
              type="text"
              value={formData.preferred_sectors}
              onChange={(e) =>
                setFormData({ ...formData, preferred_sectors: e.target.value })
              }
              placeholder="e.g., IT, Banking, Healthcare (comma-separated)"
              className="input-base w-full"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-text-primary mb-2">
              Notes
            </label>
            <textarea
              value={formData.notes}
              onChange={(e) =>
                setFormData({ ...formData, notes: e.target.value })
              }
              placeholder="Any additional investment preferences or constraints..."
              rows={4}
              className="input-base w-full resize-none"
            />
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex items-center justify-end">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="btn-primary flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {isSaving ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              Saving...
            </>
          ) : (
            <>
              <Save className="w-4 h-4" />
              Save Profile
            </>
          )}
        </button>
      </div>
    </div>
  );
}

"use client";

import { useState } from "react";
import { Settings as SettingsIcon, Save } from "lucide-react";
import { useToast } from "@/hooks/useToast";

export default function SettingsPage() {
  const { toast } = useToast();
  const [settings, setSettings] = useState({
    theme: "dark",
    currency: "INR",
    notifications: {
      enabled: true,
      priceAlerts: true,
      newsDigest: true,
    },
    security: {
      twoFactorEnabled: false,
    },
  });

  const handleToggle = (path: string) => {
    setSettings((prev) => {
      const keys = path.split(".");
      const newSettings = JSON.parse(JSON.stringify(prev));
      let current = newSettings;
      for (let i = 0; i < keys.length - 1; i++) {
        current = current[keys[i]];
      }
      current[keys[keys.length - 1]] = !current[keys[keys.length - 1]];
      return newSettings;
    });
  };

  const handleSave = () => {
    toast("Settings saved successfully", { type: "success" });
  };

  return (
    <div className="p-8 max-w-3xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <div className="flex items-center gap-3 mb-2">
          <SettingsIcon className="w-8 h-8 text-primary" />
          <h1 className="text-3xl font-bold text-text-primary">Settings</h1>
        </div>
        <p className="text-text-tertiary">
          Manage your account and application preferences
        </p>
      </div>

      {/* Display Settings */}
      <div className="card-base">
        <h2 className="text-xl font-semibold text-text-primary mb-6">
          Display
        </h2>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-text-primary">Theme</p>
              <p className="text-sm text-text-tertiary">
                Choose your preferred color scheme
              </p>
            </div>
            <select
              value={settings.theme}
              onChange={(e) =>
                setSettings({ ...settings, theme: e.target.value })
              }
              className="input-base w-32"
            >
              <option value="dark">Dark</option>
              <option value="light">Light</option>
            </select>
          </div>

          <div className="border-t border-border pt-4 flex items-center justify-between">
            <div>
              <p className="font-medium text-text-primary">Currency</p>
              <p className="text-sm text-text-tertiary">
                Display prices in your preferred currency
              </p>
            </div>
            <select
              value={settings.currency}
              onChange={(e) =>
                setSettings({ ...settings, currency: e.target.value })
              }
              className="input-base w-32"
            >
              <option value="INR">₹ INR</option>
              <option value="USD">$ USD</option>
            </select>
          </div>
        </div>
      </div>

      {/* Notification Settings */}
      <div className="card-base">
        <h2 className="text-xl font-semibold text-text-primary mb-6">
          Notifications
        </h2>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-text-primary">
                Enable Notifications
              </p>
              <p className="text-sm text-text-tertiary">
                Receive push notifications for important updates
              </p>
            </div>
            <button
              onClick={() => handleToggle("notifications.enabled")}
              className={`relative w-14 h-8 rounded-full transition-colors ${
                settings.notifications.enabled ? "bg-success" : "bg-border"
              }`}
            >
              <div
                className={`absolute top-1 w-6 h-6 bg-white rounded-full transition-transform ${
                  settings.notifications.enabled ? "translate-x-7" : "translate-x-1"
                }`}
              />
            </button>
          </div>

          {settings.notifications.enabled && (
            <>
              <div className="border-t border-border pt-4 flex items-center justify-between">
                <div>
                  <p className="font-medium text-text-primary">Price Alerts</p>
                  <p className="text-sm text-text-tertiary">
                    Get notified when stock prices hit your targets
                  </p>
                </div>
                <button
                  onClick={() => handleToggle("notifications.priceAlerts")}
                  className={`relative w-14 h-8 rounded-full transition-colors ${
                    settings.notifications.priceAlerts
                      ? "bg-success"
                      : "bg-border"
                  }`}
                >
                  <div
                    className={`absolute top-1 w-6 h-6 bg-white rounded-full transition-transform ${
                      settings.notifications.priceAlerts
                        ? "translate-x-7"
                        : "translate-x-1"
                    }`}
                  />
                </button>
              </div>

              <div className="border-t border-border pt-4 flex items-center justify-between">
                <div>
                  <p className="font-medium text-text-primary">News Digest</p>
                  <p className="text-sm text-text-tertiary">
                    Receive daily market news digest
                  </p>
                </div>
                <button
                  onClick={() => handleToggle("notifications.newsDigest")}
                  className={`relative w-14 h-8 rounded-full transition-colors ${
                    settings.notifications.newsDigest
                      ? "bg-success"
                      : "bg-border"
                  }`}
                >
                  <div
                    className={`absolute top-1 w-6 h-6 bg-white rounded-full transition-transform ${
                      settings.notifications.newsDigest
                        ? "translate-x-7"
                        : "translate-x-1"
                    }`}
                  />
                </button>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Security Settings */}
      <div className="card-base">
        <h2 className="text-xl font-semibold text-text-primary mb-6">
          Security
        </h2>

        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="font-medium text-text-primary">
                Two-Factor Authentication
              </p>
              <p className="text-sm text-text-tertiary">
                Add an extra layer of security to your account
              </p>
            </div>
            <button
              onClick={() => handleToggle("security.twoFactorEnabled")}
              className={`relative w-14 h-8 rounded-full transition-colors ${
                settings.security.twoFactorEnabled ? "bg-success" : "bg-border"
              }`}
            >
              <div
                className={`absolute top-1 w-6 h-6 bg-white rounded-full transition-transform ${
                  settings.security.twoFactorEnabled
                    ? "translate-x-7"
                    : "translate-x-1"
                }`}
              />
            </button>
          </div>

          <div className="border-t border-border pt-4">
            <button className="btn-secondary w-full">
              Change Password
            </button>
          </div>
        </div>
      </div>

      {/* Account Settings */}
      <div className="card-base">
        <h2 className="text-xl font-semibold text-text-primary mb-6">
          Account
        </h2>

        <div className="space-y-4">
          <div>
            <p className="text-sm text-text-tertiary mb-2">Email</p>
            <input
              type="email"
              value="john@email.com"
              disabled
              className="input-base opacity-50"
            />
          </div>

          <div className="border-t border-border pt-4 space-y-3">
            <button className="btn-secondary w-full">Download Your Data</button>
            <button className="btn-danger w-full">Delete Account</button>
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex items-center justify-end gap-3">
        <button className="btn-secondary">Cancel</button>
        <button onClick={handleSave} className="btn-primary flex items-center gap-2">
          <Save className="w-4 h-4" />
          Save Changes
        </button>
      </div>
    </div>
  );
}

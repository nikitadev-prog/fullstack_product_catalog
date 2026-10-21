"use client";

import { useEffect } from "react";

declare global {
  interface Window {
    Telegram?: {
      WebApp: {
        ready: () => void;
        expand: () => void;
      };
    };
  }
}

export function TelegramInit() {
  useEffect(() => {
    const app = window.Telegram?.WebApp;
    if (!app) return;
    app.ready();
    app.expand();
  }, []);
  return null;
}

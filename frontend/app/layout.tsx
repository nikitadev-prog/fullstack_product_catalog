import Link from "next/link";
import Script from "next/script";
import { TelegramInit } from "../components/TelegramInit";
import "./globals.css";

export const metadata = {
  title: "Каталог",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="ru">
      <body>
        <Script src="https://telegram.org/js/telegram-web-app.js" strategy="beforeInteractive" />
        <TelegramInit />
        <nav>
          <Link href="/">Каталог</Link>
          <Link href="/cart">Корзина</Link>
        </nav>
        {children}
      </body>
    </html>
  );
}

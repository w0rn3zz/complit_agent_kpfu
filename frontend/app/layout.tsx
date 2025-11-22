import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";

const inter = Inter({ subsets: ["latin", "cyrillic"] });

export const metadata: Metadata = {
  title: "Классификация IT-заявок | КФУ",
  description: "Система автоматической классификации заявок департамента информатизации и связи КФУ",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ru">
      <head>
        <link rel="icon" href="https://kpfu.ru/favicon.ico" />
      </head>
      <body className={inter.className}>{children}</body>
    </html>
  );
}

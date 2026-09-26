import type { ReactNode } from "react";

export const metadata = {
  title: "Training Platform",
  description: "Courses and hands-on training labs"
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

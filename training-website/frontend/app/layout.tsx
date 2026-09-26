import "./globals.css";

export const metadata = { title: "Training Platform", description: "Training delivery and hands-on lab platform" };

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return <html lang="en"><body><div className="shell">{children}</div></body></html>;
}

/**
 * 路线列表页 SEO metadata
 */
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: '苏轼行迹路线',
  description: '20条主题路线，从少年出蜀到暮年北归，完整呈现苏轼一生的行迹脉络与文学轨迹。',
  openGraph: {
    title: '苏轼行迹路线 · 行吟山河',
    description: '20条主题路线，从少年出蜀到暮年北归，完整呈现苏轼一生的行迹脉络与文学轨迹。',
  },
};

export default function RoutesLayout({ children }: { children: React.ReactNode }) {
  return children;
}

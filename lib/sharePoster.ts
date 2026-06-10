/**
 * 分享海报生成工具函数
 * 支持生成国风分享海报、保存到相册、系统原生分享
 *
 * v1.1（2026-06-10 性能优化）：
 *   把 html2canvas 改成动态 import，避免被静态打包进 /profile 首屏 bundle。
 *   profile 页面进入时不再加载 ~200KB 的 html2canvas，只有真正点击「分享」时才按需加载。
 */

/**
 * 将DOM节点转为高清图片
 * @param domId DOM节点ID
 * @returns Base64图片数据
 */
export const generateShareImage = async (domId: string): Promise<string | null> => {
  const dom = document.getElementById(domId);
  if (!dom) {
    console.error('[sharePoster] 未找到DOM节点:', domId);
    return null;
  }

  try {
    // 动态加载 html2canvas，避免阻塞首屏
    const { default: html2canvas } = await import('html2canvas');
    const canvas = await html2canvas(dom, {
      scale: 2, // 高清画质
      useCORS: true, // 解决图片跨域
      backgroundColor: '#FAF6F0', // 宣纸底色
      logging: false,
    });

    return canvas.toDataURL('image/png');
  } catch (error) {
    console.error('[sharePoster] 生成图片失败:', error);
    return null;
  }
};

/**
 * 保存图片到手机相册
 * @param base64 Base64图片数据
 * @param filename 文件名
 */
export const saveImageToAlbum = async (base64: string, filename: string = '行吟山河-分享.png'): Promise<void> => {
  try {
    const link = document.createElement('a');
    link.download = filename;
    link.href = base64;
    link.click();
  } catch (error) {
    console.error('[sharePoster] 保存图片失败:', error);
    throw error;
  }
};

/**
 * 调用手机系统原生分享
 * @param title 分享标题
 * @param text 分享文案
 * @param base64 分享图片（可选）
 */
export const nativeShare = async (title: string, text: string, base64?: string): Promise<void> => {
  if (!navigator.share) {
    throw new Error('当前设备不支持原生分享');
  }

  const shareData: ShareData = {
    title,
    text,
  };

  // 如果有图片，转换为File对象
  if (base64) {
    try {
      const blob = await fetch(base64).then(res => res.blob());
      const file = new File([blob], 'share.png', { type: 'image/png' });
      // @ts-ignore - Web Share API Level 2支持files属性
      shareData.files = [file];
    } catch (error) {
      console.warn('[sharePoster] 图片转换失败，跳过图片分享:', error);
    }
  }

  try {
    await navigator.share(shareData);
  } catch (error) {
    // 用户取消分享是正常行为，不抛出异常
    console.log('[sharePoster] 分享取消:', error);
  }
};

/**
 * 复制文案到剪贴板
 * @param text 要复制的文本
 */
export const copyToClipboard = async (text: string): Promise<void> => {
  try {
    await navigator.clipboard.writeText(text);
  } catch (error) {
    console.error('[sharePoster] 复制失败:', error);
    throw error;
  }
};

/**
 * 生成分享文案模板
 * @param type 分享类型
 * @param data 数据对象
 * @returns 分享文案
 */
export const generateShareText = (type: 'achievement' | 'checkin' | 'collection', data: {
  name?: string;
  checkinCount?: number;
  achievementCount?: number;
  totalAchievements?: number;
}): string => {
  switch (type) {
    case 'achievement':
      return `我在「行吟山河」解锁【${data.name || '成就'}】！走遍东坡足迹，感受千古文风～`;
    case 'checkin':
      return `实地打卡【${data.name || '地点'}】，与苏轼隔空相逢｜行吟山河`;
    case 'collection':
      return `累计解锁${data.achievementCount || 0}项成就，打卡${data.checkinCount || 0}处东坡足迹｜行吟山河`;
    default:
      return '行吟山河 · 读苏轼 游神州';
  }
};

/**
 * Timeline v4.0
 * 7阶段底部时间轴，motion.layoutId动画
 */

'use client';

import { motion } from 'framer-motion';
import { useSuShiStore } from '@/lib/store';
import { STAGES, Stage } from '@/types';

const STAGE_LABELS: Record<Stage, string> = {
  youth: '眉山少年',
  early_career: '入京初仕',
  first_exile: '黄州四年',
  middle_career: '翰林侍从',
  second_exile: '岭南三年',
  third_exile: '儋耳三年',
  final_journey: '北归长眠',
};

const STAGE_YEARS: Record<Stage, string> = {
  youth: '1036-1057',
  early_career: '1057-1079',
  first_exile: '1080-1084',
  middle_career: '1085-1091',
  second_exile: '1094-1097',
  third_exile: '1097-1100',
  final_journey: '1100-1101',
};

export default function Timeline() {
  const { currentStage, setCurrentStage } = useSuShiStore();

  return (
    <div className="fixed bottom-0 inset-x-0 z-40 bg-paper/95 backdrop-blur-sm border-t border-ink/10 safe-bottom">
      <div className="flex items-center gap-1 px-3 py-2 overflow-x-auto no-scrollbar">
        {STAGES.map((stage) => {
          const isActive = currentStage === stage;
          return (
            <motion.button
              key={stage}
              layoutId="active-stage"
              onClick={() => setCurrentStage(isActive ? null : stage)}
              className={`flex-shrink-0 px-3 py-1.5 rounded-full text-xs font-serif whitespace-nowrap transition-colors ${isActive ? 'bg-ink text-paper' : 'text-ink/60 hover:text-ink hover:bg-ink/5'}`}
            >
              <span className="hidden sm:inline">{STAGE_LABELS[stage]}</span>
              <span className="sm:hidden">{STAGE_LABELS[stage].slice(0, 2)}</span>
            </motion.button>
          );
        })}
      </div>

      {/* 当前阶段年份提示 */}
      {currentStage && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="text-center text-xs text-ink/40 pb-1"
        >
          {STAGE_YEARS[currentStage]}
        </motion.div>
      )}
    </div>
  );
}

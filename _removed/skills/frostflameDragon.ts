// Băng Diễm Long skills (tên tạm). No drawn effects yet (NO_VFX): only code-drawn ones (orbs, gusts, ice-shard rain),
// tinted its spirit-flame green and ice blue.
import type { SkillDef } from './types';

const dmg = (scale: number) => `-${Math.round((170 + Math.random() * 40) * scale)}`;
const FLAME = 0x8cff5a, ICE = 0x8fe3ff, FROST = '#bdf0ff';

export const FROSTFLAME_DRAGON_SKILLS: SkillDef[] = [
  { type: 'passive', name: 'Linh Hỏa Băng Tâm', desc: 'Đòn đánh có 25% làm địch Đóng Băng 1 lượt; mỗi lần làm đóng băng, +10% Công trong 2 lượt.' },
  {
    type: 'basic', name: 'Cầu Lửa Băng', desc: 'Phun 2 cầu lửa linh hồn xanh vào 1 địch: mỗi cầu 55% Công.', anim: 'attack', target: 'enemy',
    run: async ({ self, targets: [t], orb, wait }) => {
      for (let k = 0; k < 2; k++) {
        await orb(self.mouth(), t.chest(), { tint: FLAME, scale: 0.7, dur: 340 });
        t.hurt(); t.text(dmg(0.55));
        await wait(70);
      }
    },
  },
  {
    type: 'skill', name: 'Sóng Băng Diễm', desc: 'Cuốn sóng băng lửa xanh về phía trước, xuyên tối đa 3 địch: 130% Công, giảm 30% Tốc độ trong 2 lượt.',
    anim: 'cast', target: 'enemies',
    run: async ({ self, targets, gust }) => {
      await gust(self.feet(), self.facing, { reach: 540, scale: 1, tint: FLAME });
      targets.forEach(t => { t.hurt(); t.text(dmg(1.3)); t.text('Chậm', FROST); });
    },
  },
  {
    type: 'ultimate', name: 'Mưa Pha Lê Linh Hỏa', desc: 'Gọi mưa pha lê băng lẫn lửa xanh trút xuống toàn bộ địch: 3 đợt 75% Công, đóng băng 1 lượt.',
    anim: 'ultimate', target: 'enemies',
    run: async ({ targets, elementRain }) => {
      await elementRain(targets, t => { t.hurt(); t.text(dmg(0.75)); }, { tint: ICE, core: FLAME, shape: 'shard', waves: 3 });
      targets.forEach(t => t.text('Đóng Băng', FROST));
    },
  },
];

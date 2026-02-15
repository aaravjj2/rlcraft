export const builds=[{id:'demo-build',name:'Synthetic Demo Build'}];
export const mobs=Array.from({length:10},(_,i)=>({id:`mob_${i+1}`,name:`Demo Mob ${i+1}`,dimension:i%2?'overworld':'nether'}));
export const items=Array.from({length:20},(_,i)=>({id:`item_${i+1}`,name:`Demo Item ${i+1}`,mod:'demo'}));
export const structures=[{id:'tower',name:'Sky Tower',images:['tower_1.img']},{id:'dungeon',name:'Deep Dungeon',images:['dungeon_1.img']},{id:'village',name:'Safe Village',images:['village_1.img']}];

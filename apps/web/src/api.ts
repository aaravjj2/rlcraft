const API = import.meta.env.VITE_API_URL || 'http://127.0.0.1:8000';
export const BUILD_ID_KEY='demoBuildId';
export function getBuildId(){ return localStorage.getItem(BUILD_ID_KEY) || ''; }
export async function j<T>(path:string){ const r=await fetch(`${API}${path}`); if(!r.ok) throw new Error('api'); return r.json() as Promise<T>; }
export async function postImage(buildId:string,file:File){ const fd=new FormData(); fd.append('file',file); const r=await fetch(`${API}/structure-image-search?buildId=${encodeURIComponent(buildId)}`,{method:'POST',body:fd}); if(!r.ok) throw new Error('api'); return r.json(); }

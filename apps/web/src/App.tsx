import { Link, Route, Routes, useParams } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import { j, getBuildId, BUILD_ID_KEY, postImage } from './api';
import { useState } from 'react';

function Home(){
  const {data=[]}=useQuery({queryKey:['builds'],queryFn:()=>j<any[]>('/builds')});
  return <div><select data-testid='build-picker' onChange={(e)=>localStorage.setItem(BUILD_ID_KEY,e.target.value)}>{data.map(b=><option key={b.build_id} value={b.build_id}>{b.pack_name}</option>)}</select><input data-testid='search-bar'/></div>
}
function Mobs(){const id=getBuildId(); const {data=[]}=useQuery({queryKey:['mobs',id],queryFn:()=>j<any[]>(`/mobs?buildId=${id}`),enabled:!!id}); return <div>{data.map(m=><Link key={m.id} data-testid={`mobs-card-${m.id.replace(':','_')}`} to={`/mobs/${encodeURIComponent(m.id)}`}>{m.name}</Link>)}</div>}
function Items(){const id=getBuildId(); const {data=[]}=useQuery({queryKey:['items',id],queryFn:()=>j<any[]>(`/items?buildId=${id}`),enabled:!!id}); return <div>{data.map(m=><Link key={m.id} data-testid={`items-card-${m.id.replace(':','_')}`} to={`/items/${encodeURIComponent(m.id)}`}>{m.name}</Link>)}</div>}
function Structures(){const id=getBuildId(); const {data=[]}=useQuery({queryKey:['structures',id],queryFn:()=>j<any[]>(`/structures?buildId=${id}`),enabled:!!id}); return <div>{data.map(m=><Link key={m.id} data-testid={`structures-card-${m.id.replace(':','_')}`} to={`/structures/${encodeURIComponent(m.id)}`}>{m.name}</Link>)}</div>}
function Detail({kind}:{kind:string}){ const id=getBuildId(); const p=useParams(); const {data}=useQuery({queryKey:[kind,p.id,id],queryFn:()=>j<any>(`/${kind}/${p.id}?buildId=${id}`),enabled:!!id&&!!p.id}); return <div data-testid={`${kind}-detail`}>{data?.name||'loading'}</div> }
function ImageSearch(){ const [m,setM]=useState(''); const bid=getBuildId(); return <div><input data-testid='image-upload' type='file' onChange={async(e)=>{const f=e.target.files?.[0]; if(!f||!bid) return; const r=await postImage(bid,f); setM(r.matches?.[0]?.structure_key||'');}}/><div data-testid='image-match'>{m}</div></div>}

export default function App(){return <div><nav><Link data-testid='nav-home' to='/'>Home</Link><Link data-testid='nav-mobs' to='/mobs'>Mobs</Link><Link data-testid='nav-items' to='/items'>Items</Link><Link data-testid='nav-structures' to='/structures'>Structures</Link><Link data-testid='nav-image-search' to='/image-search'>Image Search</Link></nav><Routes><Route path='/' element={<Home/>}/><Route path='/mobs' element={<Mobs/>}/><Route path='/mobs/:id' element={<Detail kind='mobs'/>}/><Route path='/items' element={<Items/>}/><Route path='/items/:id' element={<Detail kind='items'/>}/><Route path='/structures' element={<Structures/>}/><Route path='/structures/:id' element={<Detail kind='structures'/>}/><Route path='/image-search' element={<ImageSearch/>}/></Routes></div>}

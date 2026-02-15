import { render, screen, waitFor } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import App from './App';

test('home smoke', async ()=>{
  global.fetch = vi.fn().mockResolvedValue({ok:true,json:async()=>[{build_id:'b1',pack_name:'Demo'}]}) as any;
  render(<QueryClientProvider client={new QueryClient()}><MemoryRouter><App/></MemoryRouter></QueryClientProvider>);
  await waitFor(()=>expect(screen.getByTestId('build-picker')).toBeTruthy());
});

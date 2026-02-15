import { test, expect } from '@playwright/test';
import path from 'path';
import { fileURLToPath } from 'url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));

test('tour flow', async ({ page }) => {
  await page.goto('/');
  await expect(page.getByTestId('build-picker')).toBeVisible();
  await page.getByTestId('build-picker').selectOption({ index: 0 });
  await page.getByTestId('nav-mobs').click();
  await page.getByTestId('mobs-card-demo_mob_1').click();
  await expect(page.getByTestId('mobs-detail')).toContainText('Demo Mob 1');
  await page.getByTestId('nav-items').click();
  await page.getByTestId('items-card-demo_item_1').click();
  await expect(page.getByTestId('items-detail')).toContainText('Demo Item 1');
  await page.getByTestId('nav-structures').click();
  await page.getByTestId('structures-card-demo_tower').click();
  await expect(page.getByTestId('structures-detail')).toContainText('Sky Tower');
  await page.getByTestId('nav-image-search').click();
  await page.getByTestId('image-upload').setInputFiles(path.resolve(__dirname,'../../../fixtures/images/tower_1.png'));
  await expect(page.getByTestId('image-match')).toContainText('demo:tower');
});

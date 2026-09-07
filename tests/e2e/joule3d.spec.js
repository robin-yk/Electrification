import { test, expect } from '@playwright/test';

test('Joule tabs open the 3D worker and import the current dense design',async({page})=>{
  const errors=[];page.on('pageerror',error=>errors.push(String(error)));
  await page.goto('/apps/joule/');
  await page.selectOption('#shape','box');
  await page.fill('#boxLength','40');await page.fill('#boxWidth','10');await page.fill('#boxHeight','2');
  await page.fill('#voidFraction','0');
  await page.fill('#pmax','30');
  await page.click('[data-tab="thermal3d"]');
  const frame=page.frameLocator('#joule3dFrame');
  await expect(frame.locator('#solve')).toBeEnabled({timeout:30000});
  await page.click('#import3d');
  await expect(frame.locator('#shape')).toHaveValue('block');
  await expect(frame.locator('#length')).toHaveValue('40');
  await expect(frame.locator('#status')).toContainText('Imported 0D');
  await frame.locator('#solve').click();
  await expect(frame.locator('#budget')).toBeVisible({timeout:30000});
  await expect(frame.locator('#savg')).toHaveText(/\d/);
  await page.click('[data-tab="calculator"]');
  await expect(page.locator('#boxLength')).toHaveValue('40');
  expect(errors).toEqual([]);
});

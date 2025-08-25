const { chromium } = require('playwright');

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();
  
  try {
    console.log('Navigating to strategy page...');
    await page.goto('http://localhost:4000/strategie/');
    
    // Wait for page to load
    await page.waitForSelector('.md-articles-grid');
    
    // Take a screenshot
    await page.screenshot({ path: 'strategy_page.png', fullPage: true });
    console.log('Screenshot saved as strategy_page.png');
    
    // Check for icons in headlines
    const headlines = await page.$$eval('.md-article-card__headline a', els => 
      els.map(el => el.textContent.trim())
    );
    
    console.log('\nArticle headlines:');
    headlines.forEach((headline, i) => {
      console.log(`${i + 1}. "${headline}"`);
    });
    
    // Check the CSS of article cards
    const cardStyles = await page.$$eval('.md-article-card', els => 
      els.map(el => {
        const styles = window.getComputedStyle(el);
        return {
          display: styles.display,
          flexDirection: styles.flexDirection,
          width: styles.width,
          height: styles.height,
          minHeight: styles.minHeight
        };
      })
    );
    
    console.log('\nCard styles:');
    cardStyles.forEach((style, i) => {
      console.log(`Card ${i + 1}:`, style);
    });
    
    // Check grid styles
    const gridStyles = await page.$eval('.md-articles-grid', el => {
      const styles = window.getComputedStyle(el);
      return {
        display: styles.display,
        gridTemplateColumns: styles.gridTemplateColumns,
        gap: styles.gap
      };
    });
    
    console.log('\nGrid styles:', gridStyles);
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
})();
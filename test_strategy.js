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
    
    // Check for all elements on the first card to find the black box
    const firstCardElements = await page.$eval('.md-article-card', el => {
      const allChildren = el.querySelectorAll('*');
      const elements = [];
      
      // Check all children and pseudo-elements
      allChildren.forEach((child, i) => {
        const styles = window.getComputedStyle(child);
        const beforeStyles = window.getComputedStyle(child, ':before');
        const afterStyles = window.getComputedStyle(child, ':after');
        
        elements.push({
          element: i + 1,
          tagName: child.tagName,
          className: child.className,
          styles: {
            position: styles.position,
            background: styles.background,
            backgroundColor: styles.backgroundColor,
            width: styles.width,
            height: styles.height,
            top: styles.top,
            left: styles.left,
            zIndex: styles.zIndex,
            display: styles.display
          },
          before: {
            content: beforeStyles.content,
            display: beforeStyles.display,
            position: beforeStyles.position,
            background: beforeStyles.background,
            backgroundColor: beforeStyles.backgroundColor,
            width: beforeStyles.width,
            height: beforeStyles.height
          },
          after: {
            content: afterStyles.content,
            display: afterStyles.display,
            position: afterStyles.position,
            background: afterStyles.background,
            backgroundColor: afterStyles.backgroundColor,
            width: afterStyles.width,
            height: afterStyles.height
          }
        });
      });
      
      return elements;
    });
    
    console.log('\nFirst card DOM structure:');
    firstCardElements.forEach(el => {
      if (el.styles.position === 'absolute' || 
          el.styles.backgroundColor.includes('black') || 
          el.styles.backgroundColor.includes('rgb(0, 0, 0)') ||
          el.before.display !== 'none' ||
          el.after.display !== 'none') {
        console.log('POTENTIAL BLACK BOX:', el);
      }
    });
    
    // Look for specific overlay elements
    const overlayElements = await page.$$eval('*', els => {
      return els.filter(el => {
        const styles = window.getComputedStyle(el);
        return (
          styles.position === 'absolute' && 
          (styles.backgroundColor.includes('black') || 
           styles.backgroundColor.includes('rgb(0, 0, 0)') ||
           styles.backgroundColor.includes('rgba(0, 0, 0'))
        );
      }).map(el => ({
        tagName: el.tagName,
        className: el.className,
        id: el.id,
        textContent: el.textContent.slice(0, 50),
        styles: {
          position: window.getComputedStyle(el).position,
          backgroundColor: window.getComputedStyle(el).backgroundColor,
          width: window.getComputedStyle(el).width,
          height: window.getComputedStyle(el).height,
          top: window.getComputedStyle(el).top,
          left: window.getComputedStyle(el).left,
          zIndex: window.getComputedStyle(el).zIndex
        }
      }));
    });
    
    console.log('\nBlack/Dark overlay elements found:');
    overlayElements.forEach((el, i) => {
      console.log(`Overlay ${i + 1}:`, el);
    });
    
  } catch (error) {
    console.error('Error:', error);
  } finally {
    await browser.close();
  }
})();
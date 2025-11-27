# GitHub Pages Deployment Guide

## Setup Instructions

### 1. Update Configuration

Replace `YOUR_USERNAME` and `YOUR_REPO_NAME` in the following files:

**package.json:**
```json
"homepage": "https://YOUR_USERNAME.github.io/YOUR_REPO_NAME"
```

**vite.config.js:**
```javascript
base: '/YOUR_REPO_NAME/'
```

### 2. Install Dependencies

```bash
cd motif-react-app
npm install
```

This will install the `gh-pages` package needed for deployment.

### 3. Build and Deploy

```bash
npm run deploy
```

This command will:
1. Build your React app (`npm run build`)
2. Deploy the `dist` folder to the `gh-pages` branch
3. Push to GitHub

### 4. Configure GitHub Repository

1. Go to your GitHub repository
2. Navigate to **Settings** → **Pages**
3. Under "Source", select:
   - Branch: `gh-pages`
   - Folder: `/ (root)`
4. Click **Save**

### 5. Access Your Site

Your site will be available at:
```
https://YOUR_USERNAME.github.io/YOUR_REPO_NAME
```

It may take a few minutes for the site to go live after the first deployment.

## Updating the Site

Whenever you make changes:

```bash
npm run deploy
```

This will rebuild and redeploy automatically.

## Important Notes

### Data Files
Your data files need to be accessible. Make sure:
- `data/` folder is in the `public/` directory, OR
- Update data loading paths to use the correct base URL

### Router Configuration
The app uses React Router with BrowserRouter. For GitHub Pages, you might need to:
- Use HashRouter instead, OR
- Add a 404.html redirect (see below)

### 404 Handling (Optional)

Create `motif-react-app/public/404.html`:

```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Redirecting...</title>
    <script>
      sessionStorage.redirect = location.href;
    </script>
    <meta http-equiv="refresh" content="0;URL='/YOUR_REPO_NAME'">
  </head>
  <body></body>
</html>
```

## Troubleshooting

### Blank Page
- Check browser console for errors
- Verify `base` path in vite.config.js matches your repo name
- Ensure all asset paths are relative

### 404 on Refresh
- Use HashRouter instead of BrowserRouter, OR
- Implement the 404.html redirect solution above

### Data Not Loading
- Move data files to `public/data/`
- Update data loading paths to use `import.meta.env.BASE_URL`

## Alternative: Using HashRouter

If you encounter routing issues, switch to HashRouter:

**src/App.jsx:**
```javascript
import { HashRouter, Routes, Route, Link } from 'react-router-dom'

function App() {
  return (
    <HashRouter>
      {/* rest of your app */}
    </HashRouter>
  )
}
```

With HashRouter, URLs will look like: `https://username.github.io/repo/#/motifs`

## Local Testing

Test the production build locally before deploying:

```bash
npm run build
npm run preview
```

This will serve the built files and help catch any issues.

# GitHub Pages Deployment Guide

## Automatic Deployment with GitHub Actions

Your repository is configured to automatically deploy to GitHub Pages using GitHub Actions whenever you push changes to the `main` branch.

## Setup Instructions

### 1. Enable GitHub Pages

1. Go to your repository on GitHub: `https://github.com/hrishi-verma/motif-based-graph-compression`
2. Click **Settings** (top menu)
3. Click **Pages** (left sidebar under "Code and automation")
4. Under "Build and deployment":
   - **Source**: Select "GitHub Actions"
5. Save (if needed)

### 2. Push Your Code

```bash
git add .
git commit -m "Add GitHub Actions deployment"
git push origin main
```

### 3. Monitor Deployment

1. Go to the **Actions** tab in your repository
2. You'll see the "Deploy to GitHub Pages" workflow running
3. Wait for it to complete (green checkmark)

### 4. Access Your Site

Your site will be available at:
```
https://hrishi-verma.github.io/motif-based-graph-compression
```

## How It Works

The `.github/workflows/deploy.yml` file automatically:
1. Triggers on push to `main` branch (when `motif-react-app/` changes)
2. Installs dependencies
3. Builds the React app
4. Deploys to GitHub Pages

## Making Updates

Just push your changes to the `main` branch:

```bash
cd motif-react-app
# Make your changes
git add .
git commit -m "Update feature"
git push origin main
```

The site will automatically rebuild and redeploy!

## Important Notes

### Data Files

Your data files need to be accessible. Options:

1. **Move to public folder:**
   ```bash
   mv data motif-react-app/public/data
   ```

2. **Update data loading paths** in your hooks to use:
   ```javascript
   const dataPath = `${import.meta.env.BASE_URL}data/filename.json`
   ```

### Router Configuration

The app uses BrowserRouter. For GitHub Pages, you might need to handle 404s.

**Option 1: Use HashRouter** (Recommended for GitHub Pages)

Update `motif-react-app/src/App.jsx`:
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

URLs will look like: `https://hrishi-verma.github.io/motif-based-graph-compression/#/motifs`

**Option 2: Add 404 redirect**

Create `motif-react-app/public/404.html`:
```html
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <title>Redirecting...</title>
    <script>
      var pathSegmentsToKeep = 1;
      var l = window.location;
      l.replace(
        l.protocol + '//' + l.hostname + (l.port ? ':' + l.port : '') +
        l.pathname.split('/').slice(0, 1 + pathSegmentsToKeep).join('/') + '/?/' +
        l.pathname.slice(1).split('/').slice(pathSegmentsToKeep).join('/').replace(/&/g, '~and~') +
        (l.search ? '&' + l.search.slice(1).replace(/&/g, '~and~') : '') +
        l.hash
      );
    </script>
  </head>
  <body></body>
</html>
```

## Local Testing

Test the production build locally:

```bash
cd motif-react-app
npm run build
npm run preview
```

Visit `http://localhost:4173` to test.

## Troubleshooting

### Workflow Fails
- Check the Actions tab for error messages
- Ensure `package-lock.json` exists (run `npm install` if not)
- Verify Node version compatibility

### Blank Page
- Check browser console for errors
- Verify `base` path in `vite.config.js` is correct: `/motif-based-graph-compression/`
- Check that data files are accessible

### 404 on Refresh
- Switch to HashRouter (see above)
- Or implement the 404.html redirect

### Data Not Loading
- Move data files to `motif-react-app/public/data/`
- Update paths to use `import.meta.env.BASE_URL`

## Manual Deployment (Alternative)

If you prefer manual control, you can trigger deployment manually:

1. Go to **Actions** tab
2. Select "Deploy to GitHub Pages" workflow
3. Click "Run workflow"
4. Select branch and click "Run workflow"

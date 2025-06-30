import { build } from "esbuild";
import { join, extname, relative, dirname, basename } from "path";
import { readdirSync, mkdirSync } from "fs";

const inputDir = "./src";
const outputDir = "./static/js";

const extensions = [".js", ".ts", ".jsx", ".tsx"];

/**
 * Recursively collect all files matching target extensions
 */
function getFiles(dir) {
  const entries = readdirSync(dir, { withFileTypes: true });

  return entries.flatMap((entry) => {
    const fullPath = join(dir, entry.name);
    if (entry.isDirectory()) {
      return getFiles(fullPath);
    } else if (extensions.includes(extname(entry.name))) {
      return [fullPath];
    } else {
      return [];
    }
  });
}

/**
 * Convert source file path to output file path, maintaining structure
 */
function getOutPath(filePath) {
  const relativePath = relative(inputDir, filePath);
  const ext = extname(relativePath);
  const base = relativePath.slice(0, -ext.length);
  return join(outputDir, `${base}.bundle.js`);
}

// Collect and build all matching files
const allFiles = getFiles(inputDir);

allFiles.forEach(async (filePath) => {
  const outPath = getOutPath(filePath);

  // Ensure output directory exists
  mkdirSync(dirname(outPath), { recursive: true });

  build({
    entryPoints: [filePath],
    bundle: true,
    outfile: outPath,
    format: "iife",
    platform: "browser",
    minify: true,
    jsx: "automatic",
    target: ["es2017"],
    // external: ['react', 'react-dom'], // optional if using shared bundle
    globalName: basename(filePath, extname(filePath)), // optional
  })
    .then(() => {
      console.log(`✅ Built: ${filePath} → ${outPath}`);
    })
    .catch((err) => {
      console.error(`❌ Error in ${filePath}:`, err.message);
    });
});

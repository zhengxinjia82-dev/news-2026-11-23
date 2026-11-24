// make.fun entrypoint for news-image-20261123.
// Node 22 stdlib only. Reads the pre-rendered front page (entry.png),
// validates it is a real PNG of the required size, and writes it to
// /output/entry.png byte-for-byte.
import { readFileSync, writeFileSync, mkdirSync, existsSync } from "node:fs";
import { createHash } from "node:crypto";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const HERE = dirname(fileURLToPath(import.meta.url));
const SRC = join(HERE, "entry.png");
const OUT_DIR = "/output";
const OUT = join(OUT_DIR, "entry.png");

const PNG_MAGIC = Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]);

if (!existsSync(SRC)) {
  throw new Error(`entry.png not found next to main.ts (${SRC})`);
}
const bytes = readFileSync(SRC);
if (!bytes.subarray(0, 8).equals(PNG_MAGIC)) {
  throw new Error("entry.png is not a PNG file (bad magic bytes)");
}
if (bytes.length > 1024 * 1024) {
  throw new Error(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
}
// PNG IHDR: width and height are big-endian uint32 at offsets 16 and 20.
// The 4 bytes before them (offsets 12-15) must be the chunk type "IHDR".
const chunkType = bytes.subarray(12, 16).toString("latin1");
if (chunkType !== "IHDR") {
  throw new Error(`entry.png has no IHDR chunk (found ${JSON.stringify(chunkType)})`);
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width !== 1024 || height !== 1024) {
  throw new Error(`entry.png is ${width}x${height}, expected 1024x1024`);
}

mkdirSync(OUT_DIR, { recursive: true });
writeFileSync(OUT, bytes);

const check = readFileSync(OUT);
if (!check.equals(bytes)) {
  throw new Error("output bytes differ from entry.png");
}
const sha = createHash("sha256").update(bytes).digest("hex");
console.log(`wrote ${OUT} (${bytes.length} bytes, sha256 ${sha})`);

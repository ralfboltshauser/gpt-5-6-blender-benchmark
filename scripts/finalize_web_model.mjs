import { readFile, rename, stat, writeFile } from "node:fs/promises";


const output = "site/assets/models/sol-ultra-diorama.glb";
const optimized = "site/assets/models/sol-ultra-diorama.optimized.glb";
const reportPath = "site/assets/models/sol-ultra-diorama.json";

await rename(optimized, output);
const report = JSON.parse(await readFile(reportPath, "utf8"));
report.optimized_glb_bytes = (await stat(output)).size;
await writeFile(reportPath, `${JSON.stringify(report, null, 2)}\n`);

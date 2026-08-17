import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.ts'],
  // Dual ESM + CJS so the package works from `import` and `require` alike.
  format: ['esm', 'cjs'],
  dts: true,
  sourcemap: true,
  clean: true,
  treeshake: true,
  target: 'es2022',
  outExtension: ({ format }) => ({ js: format === 'cjs' ? '.cjs' : '.js' }),
});

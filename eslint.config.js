// SPDX-License-Identifier: Apache-2.0
module.exports = [
  {
    files: ['**/*.js', '**/*.mjs', '**/*.cjs'],
    rules: {
      'indent': ['error', 2],
      'linebreak-style': ['error', 'unix'],
      'quotes': ['error', 'single'],
      'semi': ['error', 'always'],
      'no-console': 'warn',
    },
    languageOptions: {
      ecmaVersion: 2021,
      sourceType: 'module',
      globals: {
        browser: true,
        node: true,
        es2021: true,
      },
    },
  },
];
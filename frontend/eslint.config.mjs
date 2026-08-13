import nextVitals from "eslint-config-next/core-web-vitals";

const config = [
  ...nextVitals,
  {
    ignores: [".next/**", "node_modules/**"],
    rules: {
      "@typescript-eslint/no-explicit-any": "off",
    },
  },
];

export default config;

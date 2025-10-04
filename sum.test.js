const sum = require("./sum");

test("sum adds numbers", () => {
  expect(sum(1, 2)).toBe(3);
  expect(sum(-1, 2)).toBe(1);
  expect(sum(0, 0)).toBe(0);
});

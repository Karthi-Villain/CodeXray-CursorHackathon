// Tiny string + math utilities used to smoke-test the JS runner.

export function add(a, b) {
  return a + b;
}

export function divide(a, b) {
  if (b === 0) {
    throw new Error("cannot divide by zero");
  }
  return a / b;
}

export function isPalindrome(text) {
  if (typeof text !== "string") {
    throw new TypeError("text must be a string");
  }
  const cleaned = text.toLowerCase().replace(/[^a-z0-9]/g, "");
  return cleaned === [...cleaned].reverse().join("");
}

export function fizzbuzz(n) {
  if (n <= 0) return [];
  const out = [];
  for (let i = 1; i <= n; i++) {
    if (i % 15 === 0) out.push("FizzBuzz");
    else if (i % 3 === 0) out.push("Fizz");
    else if (i % 5 === 0) out.push("Buzz");
    else out.push(String(i));
  }
  return out;
}

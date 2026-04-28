// Tiny calculator + string utilities used to smoke-test the Java runner.

public class Calculator {

    public static int add(int a, int b) {
        return a + b;
    }

    public static double divide(double a, double b) {
        if (b == 0) {
            throw new ArithmeticException("cannot divide by zero");
        }
        return a / b;
    }

    public static boolean isPalindrome(String text) {
        if (text == null) {
            throw new IllegalArgumentException("text must not be null");
        }
        StringBuilder sb = new StringBuilder();
        for (char c : text.toCharArray()) {
            if (Character.isLetterOrDigit(c)) {
                sb.append(Character.toLowerCase(c));
            }
        }
        String cleaned = sb.toString();
        String reversed = new StringBuilder(cleaned).reverse().toString();
        return cleaned.equals(reversed);
    }

    public static String[] fizzbuzz(int n) {
        if (n <= 0) return new String[0];
        String[] out = new String[n];
        for (int i = 1; i <= n; i++) {
            if (i % 15 == 0) out[i - 1] = "FizzBuzz";
            else if (i % 3 == 0) out[i - 1] = "Fizz";
            else if (i % 5 == 0) out[i - 1] = "Buzz";
            else out[i - 1] = String.valueOf(i);
        }
        return out;
    }
}

#include <iostream>
using namespace std;

void pattern(int n) {
    for (int i = 0; i < n; i++) {

        // Spaces
        for (int j = 0; j < n - i - 1; j++)
            cout << " ";

        char ch = 'A';

        // Increasing
        for (int k = 0; k <= i; k++)
            cout << ch++;

        // Move back two characters
        ch -= 2;

        // Decreasing
        for (int l = 0; l < i; l++)
            cout << ch--;

        cout << endl;
    }
}

int main() {
    int n;
    cin >> n;
    pattern(n);
    return 0;
}
#include <iostream>
using namespace std;

void pattern(int n) {
    for (int i = 0; i < n; i++) {

        char ch = 'A' + (n - i - 1);

        for (int j = 0; j <= i; j++) {
            cout << ch << " ";
            ch++;
        }

        cout << endl;
    }
}

int main() {
    int n;
    cin >> n;
    pattern(n);
    return 0;
}
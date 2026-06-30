#include <iostream>
using namespace std;

void pattern4(int n) {
    for (int i = n; i >= 0; i--) {
        for (int j = i; j >0; j--) {
            cout << "*";
        }
        cout << "\n";
    }
}

int main() {
    int n;
    cin >> n;
    pattern4(n);
    return 0;
}
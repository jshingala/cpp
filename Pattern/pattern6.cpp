#include <iostream>
using namespace std;

void pattern6(int n) {
    for (int i = n; i >= 0; i--) {
        for (int j = i; j >0; j--) {
            cout << n - j+1  ;
        }
        cout << "\n";
        n--;
    }
}

int main() {
    int n;
    cin >> n;
    pattern6(n);
    return 0;
}
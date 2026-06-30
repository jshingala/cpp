#include <iostream>
using namespace std;

void pattern6(int n) {
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n - 1- i; j++) {
            cout << " " ;
        }
        for (int k = 0; k<= 2 * i; k++){
            cout<<"*";
        }
        cout << "\n";
    }
}

int main() {
    int n;
    cin >> n;
    pattern6(n);
    return 0;
}
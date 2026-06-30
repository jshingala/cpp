#include <iostream>
using namespace std;

void pattern6(int n) {
    for (int i =n; i > 0; i--){
        for (int j = n-i; j >0; j--){
            cout <<" ";
        }
        for(int k = (i*2)-1;k>0;k--)
        {
            cout<<"*";
        }
        cout <<"\n";
    }
}
int main() {
    int n;
    cin >> n;
    pattern6(n);
    return 0;
}